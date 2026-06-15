from typing import List

class RecursiveTextChunker:
    def __init__(self, chunk_size: int = 2000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text: str) -> List[str]:
        """
        Recursively splits text into chunks.
        First attempts to split by double newline, then single newline,
        then sentences, then words.
        """
        if not text:
            return []

        separators = ["\n\n", "\n", ". ", "? ", "! ", " ", ""]
        return self._split(text, separators, self.chunk_size, self.overlap)

    def _split(self, text: str, separators: List[str], max_size: int, overlap: int) -> List[str]:
        # If the text is small enough, it's a single chunk
        if len(text) <= max_size:
            return [text]

        # Find the first separator to use
        separator = separators[0]
        next_separators = separators[1:]
        
        splits = text.split(separator)
        
        # Recombine splits into chunks of appropriate size
        chunks = []
        current_chunk = []
        current_length = 0

        for s in splits:
            item = s + (separator if s != splits[-1] else "")
            item_len = len(item)

            if item_len > max_size:
                # If this item itself is too large, split it recursively using remaining separators
                if current_chunk:
                    chunks.append("".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                if next_separators:
                    sub_chunks = self._split(s, next_separators, max_size, overlap)
                    chunks.extend(sub_chunks)
                else:
                    # No more separators, must force-split characters
                    for i in range(0, len(s), max_size - overlap):
                        chunks.append(s[i:i + max_size])
            else:
                if current_length + item_len > max_size:
                    # Store current chunk
                    chunks.append("".join(current_chunk))
                    
                    # Backtrack for overlap
                    # Find splits that fit within overlap limit
                    overlap_chunk = []
                    overlap_len = 0
                    for prev in reversed(current_chunk):
                        if overlap_len + len(prev) <= overlap:
                            overlap_chunk.insert(0, prev)
                            overlap_len += len(prev)
                        else:
                            break
                    
                    current_chunk = overlap_chunk
                    current_length = overlap_len
                
                current_chunk.append(item)
                current_length += item_len

        if current_chunk:
            chunks.append("".join(current_chunk))

        # Filter out empty or whitespace-only chunks
        return [c.strip() for c in chunks if c.strip()]
