"""Handwritten protobuf encoder for the D4 loot filter format.

Ported from the inline JS in index.html. Field numbers, nesting, and magic
constants are reverse-engineered from live in-game exports and are
load-bearing; refactors must byte-match old vs. new output.
"""

from __future__ import annotations


def encode_varint(value: int) -> bytes:
    assert value >= 0
    out = bytearray()
    while True:
        out.append(value & 0x7F)
        value >>= 7
        if value == 0:
            break
    for i in range(len(out) - 1):
        out[i] |= 0x80
    return bytes(out)


def field_varint(field: int, value: int) -> bytes:
    return encode_varint(field << 3) + encode_varint(value)


def field_32bit(field: int, value: int) -> bytes:
    return encode_varint((field << 3) | 5) + value.to_bytes(4, "little")


def field_blob(field: int, data: bytes) -> bytes:
    return encode_varint((field << 3) | 2) + encode_varint(len(data)) + data


def field_string(field: int, value: str) -> bytes:
    return field_blob(field, value.encode())


def cond_rarity(mask: int) -> bytes:
    return field_blob(4, field_varint(1, 1) + field_varint(4, mask))


def cond_greater_affix(n: int) -> bytes:
    return field_blob(4, field_varint(1, 3) + field_varint(6, n))


def cond_codex() -> bytes:
    return field_blob(4, field_varint(1, 4) + field_varint(4, 1) + field_varint(6, 1))


def cond_affixes(ids: list[int], n: int) -> bytes:
    inner = field_varint(1, 6)
    for id_ in ids:
        inner += field_32bit(2, id_)
    inner += field_varint(4, n)
    return field_blob(4, inner)


def cond_types(ids: list[int]) -> bytes:
    inner = field_varint(1, 5)
    for id_ in ids:
        inner += field_32bit(2, id_)
    return field_blob(4, inner)


def make_rule(name: str, visibility: int, conditions: list[bytes], color: int | None = None) -> bytes:
    if color is None:
        from . import data

        color = data.C_DEF
    rule = field_string(1, name) + field_varint(2, visibility) + field_32bit(3, color)
    for cond in conditions:
        rule += cond
    rule += field_varint(5, 1)
    return field_blob(1, rule)


def make_filter(name: str, rules: list[bytes]) -> bytes:
    out = bytearray()
    for rule in rules:
        out += rule
    out += field_string(2, name)
    out += field_varint(3, len(rules))
    out += field_varint(4, 1)
    return bytes(out)


def to_base64(data: bytes) -> str:
    import base64

    return base64.b64encode(data).decode()
