from flask import Flask, request, render_template, send_file
from io import BytesIO
import heapq
from collections import Counter
import time
from tabulate import tabulate

app = Flask(__name__)

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(data):
    frequency = Counter(data)
    heap = [HuffmanNode(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = HuffmanNode(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)
    return heap[0], frequency

def huffman_codes(node, prefix="", codebook={}):
    if node is not None:
        if node.char is not None:
            codebook[node.char] = prefix
        huffman_codes(node.left, prefix + "0", codebook)
        huffman_codes(node.right, prefix + "1", codebook)
    return codebook

def huffman_encode(data):
    root, frequency = build_huffman_tree(data)
    codebook = huffman_codes(root)
    encoded_data = ''.join(codebook[char] for char in data)
    return encoded_data, codebook, frequency

def huffman_decode(encoded_data, codebook):
    decoded_data = ""
    current_code = ""
    for bit in encoded_data:
        current_code += bit
        if current_code in codebook.values():
            decoded_char = [char for char, code in codebook.items() if code == current_code][0]
            decoded_data += decoded_char
            current_code = ""
    return decoded_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    data = file.read().decode('utf-8')
    
    # Encoding
    start_time = time.time()
    encoded_data, codebook, frequency = huffman_encode(data)
    encoding_time = time.time() - start_time

    # Store encoded data temporarily
    global encoded_file_data
    encoded_file_data = encoded_data

    # Decoding 
    start_time = time.time()
    decoded_data = huffman_decode(encoded_data, codebook)
    decoding_time = time.time() - start_time

    table_data = []
    for char in codebook:
        freq = frequency[char]
        code = codebook[char]
        size_in_bits = freq * len(code)  # Size in bits is frequency * code length
        table_data.append([char, freq, code, size_in_bits])
    
    headers = ["Character", "Frequency", "Code", "Size in Bits"]
    table = tabulate(table_data, headers=headers, tablefmt="html")

    # Original data size
    original_data_size = len(data)
    original_data_size_in_bits = original_data_size * 8  # Each character is 8 bits

    # Encoded data size
    encoded_data_size = len(encoded_data)

    return render_template('download.html', table=table, original_size=original_data_size_in_bits, encoded_size=encoded_data_size)

@app.route('/download', methods=['GET'])
def download_file():
    if not encoded_file_data:
        return "Encoded file not found"
    
    bytes_io = BytesIO()
    bytes_io.write(encoded_file_data.encode('utf-8'))
    bytes_io.seek(0)
    
    return send_file(bytes_io, as_attachment=True, download_name='encoded.txt', mimetype='text/plain')

if __name__ == "__main__":
    app.run(debug=True)
