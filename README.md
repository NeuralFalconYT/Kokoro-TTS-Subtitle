# Run Kokoro TTS V1.0

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NeuralFalconYT/kokoro_v1/blob/main/Kokoro_82M_v1_0.ipynb) <br>
[![HuggingFace Space Demo](https://img.shields.io/badge/🤗-Space%20demo-yellow)](https://huggingface.co/spaces/NeuralFalcon/KOKORO-TTS-1.0)


## Installation

### Prerequisites
- Minimum Python 3.10
- Git
- (Optional) Virtual Environment for dependency isolation

### Steps to Install and Run

1. **Clone the Repository**
   ```sh
   git clone https://github.com/NeuralFalconYT/kokoro_v1.git
   cd kokoro_v1
   ```

2. **(Optional) Create and Activate a Virtual Environment**
   - **Windows:**
     ```sh
     python -m venv myenv
     myenv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```sh
     python3 -m venv myenv
     source myenv/bin/activate
     ```

3. **Install PyTorch**
- **Forcefully install Torch with CUDA. If you did not, then requirements.txt will install the CPU version [It's happening with my system.]**
  - Check CUDA Version (for GPU setup):
    ```bash
    nvcc --version
    ```
    Find your CUDA version example ```11.8```

  - Visit [PyTorch Get Started](https://pytorch.org/get-started/locally/) and install the version compatible with your CUDA setup.:<br>
    - For CUDA 11.8:
    ```
    pip install torch  --index-url https://download.pytorch.org/whl/cu118
    ```
    - For CUDA 12.1:
    ```
    pip install torch  --index-url https://download.pytorch.org/whl/cu121
    ```
    - For CUDA 12.4:
    ```
    pip install torch  --index-url https://download.pytorch.org/whl/cu124
    ```
    
4. **Install Dependencies**
   - **Windows/Mac/Linux:**
     ```sh
     pip install -r requirements.txt
     ```

4. **Run the Application**<br>
   If you used a virtual environment, make sure you enabled it.
   - **Windows/Mac/Linux:**
     ```sh
     python app.py
     ```
   Or,<br>
   ```python one_clicker.py```<br>
   Then, double-click on `run_app.bat` (Windows) to execute the script.


## License
[Kokoro model](https://huggingface.co/hexgrad/Kokoro-82M) is licensed under the [Apache License 2.0]
## Credits
[Kokoro HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M)
