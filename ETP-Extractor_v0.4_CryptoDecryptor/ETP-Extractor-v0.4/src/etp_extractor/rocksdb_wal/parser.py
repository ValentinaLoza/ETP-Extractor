from __future__ import annotations

import struct
from pathlib import Path
from typing import Iterator


def _read_varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while offset < len(data):
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
        shift += 7
    raise ValueError("Truncated varint")


def iter_logical_records(path: Path) -> Iterator[bytes]:
    data = path.read_bytes()
    offset = 0
    fragmented = bytearray()

    while offset + 7 <= len(data):
        remaining = 32768 - (offset % 32768)
        if remaining < 7:
            offset += remaining
            continue

        _, length, record_type = struct.unpack_from("<IHB", data, offset)
        offset += 7

        if length == 0 and record_type == 0:
            if offset % 32768:
                offset += 32768 - (offset % 32768)
            continue

        payload = data[offset : offset + length]
        offset += length
        if len(payload) != length:
            break

        if record_type == 1:  # FULL
            yield payload
        elif record_type == 2:  # FIRST
            fragmented = bytearray(payload)
        elif record_type == 3:  # MIDDLE
            fragmented.extend(payload)
        elif record_type == 4:  # LAST
            fragmented.extend(payload)
            yield bytes(fragmented)
            fragmented.clear()


def parse_write_batch(payload: bytes) -> list[tuple[int, str, bytes, bytes | None]]:
    if len(payload) < 12:
        return []

    sequence = struct.unpack_from("<Q", payload, 0)[0]
    count = struct.unpack_from("<I", payload, 8)[0]
    offset = 12
    operations: list[tuple[int, str, bytes, bytes | None]] = []

    for _ in range(count):
        tag = payload[offset]
        offset += 1
        key_length, offset = _read_varint(payload, offset)
        key = payload[offset : offset + key_length]
        offset += key_length

        if tag == 1:
            value_length, offset = _read_varint(payload, offset)
            value = payload[offset : offset + value_length]
            offset += value_length
            operations.append((sequence, "put", key, value))
        elif tag == 0:
            operations.append((sequence, "delete", key, None))
        else:
            raise ValueError(f"Unsupported RocksDB write-batch tag: {tag}")
        sequence += 1

    return operations


def load_latest_values(database_directory: Path) -> dict[bytes, bytes]:
    values: dict[bytes, bytes] = {}
    for log_path in sorted(database_directory.glob("*.log")):
        for record in iter_logical_records(log_path):
            for _, operation, key, value in parse_write_batch(record):
                if operation == "put" and value is not None:
                    values[key] = value
                else:
                    values.pop(key, None)
    return values
