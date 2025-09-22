def segment(segment: bytes, color: tuple[int, int, int]) -> None:
    capped_color = [max(0, min(c, 255)) for c in color]
    data = (
        b"\x33\x05\x15\x01"
        + bytes(capped_color)
        + b"\x00\x00\x00\x00\x00"
        + segment
        + b"\x00\x00\x00\x00\x00"
    )
    return data

def main() -> None:
    segment_data = b"\x00\x01\x02\x03\x04"
    color = (255, 0, 0)  # Red color
    data = segment(segment_data, color)
    print(data.decode('utf-8'))  # Decode data to readable text

if __name__ == "__main__":
    main()