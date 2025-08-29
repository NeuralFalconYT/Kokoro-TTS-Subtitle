# Kokoro TTS V1.0 with Subtitle & SRT Dubbing

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NeuralFalconYT/Kokoro-TTS-Subtitle/blob/main/Kokoro_82M_v1_0.ipynb) <br>
[![HuggingFace Space Demo](https://img.shields.io/badge/🤗-Space%20demo-yellow)](https://huggingface.co/spaces/NeuralFalcon/Kokoro-TTS-Subtitle)

Alternative ways to use Kokoro-TTS [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx), [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI), [kokoro](https://github.com/hexgrad/kokoro)


![app](https://github.com/user-attachments/assets/a33decd0-6e60-4fda-aceb-9bd4485b8ca9)

![srt dub](https://github.com/user-attachments/assets/04a0a26f-ca3a-404a-b642-ccdf23938e9a)

## Installation

### Prerequisites
- At least Python 3.10
- Git
- (Optional) Virtual Environment for dependency isolation

### Steps to Install and Run

1. **Clone the Repository**
   ```sh
   https://github.com/NeuralFalconYT/Kokoro-TTS-Subtitle.git
   cd Kokoro-TTS-Subtitle
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



---

4. **Install eSpeak NG**

- **For Windows:**
  1. Download the eSpeak NG 1.50 release from the [eSpeak NG GitHub Releases](https://github.com/espeak-ng/espeak-ng/releases/tag/1.50). [Or, You can try eSpeak NG latest Version]
  2. Locate and download the file named **`espeak-ng-X64.msi`**.
  3. Run the installer and follow the installation steps. Ensure that you install eSpeak NG in the default directory:
     ```
     C:\Program Files\eSpeak NG
     ```
     > **Note:** This default path is required for the application to locate eSpeak NG properly.

- **For Linux:**
  1. Open your terminal.
  2. Install eSpeak NG using the following command:
     ```bash
     sudo apt-get -qq -y install espeak-ng > /dev/null 2>&1
     ```
     > **Note:** This command suppresses unnecessary output for a cleaner installation process.

---

5. **Run the Application**<br>
   If you used a virtual environment, make sure you enabled it.
   - **Windows/Mac/Linux:**
     ```sh
     python beta.py
     ```
   Or,<br>
   ```
   python one_clicker.py
   ```
   Then, double-click on `run_app.bat` (Windows) to execute the script.
<br>

6. **Use Kokoko TTS Gradio app as an API in your other project:**  
   Check out ```scripts/api.py``` Code

###### Uninstallation Guide for Kokoro v1.0

##### If You Used a Virtual Environment:
1. Simply delete the `kokoro_v1` folder from your project directory.

##### If You Did Not Use a Virtual Environment:
1. Inside the `kokoro_v1` directory, run the following command to uninstall dependencies:
   ```bash
   pip uninstall -r requirements.txt
   ```
2. Uninstall PyTorch:
   ```bash
   pip uninstall torch
   ```
#### To clear the HuggingFace cache models:
   - Navigate to `C:\Users\<username>\.cache\huggingface\hub`
   - Delete the contents of the `hub` folder.
That's it! You've successfully removed everything.







### 🛠️ Fix for Japanese Audio Generation Error

If you encounter an error while generating Japanese audio, try the following steps:

1. **Uninstall existing `unidic`:**

   ```bash
   pip uninstall unidic -y
   ```

2. **Reinstall `unidic`:**

   ```bash
   pip install unidic
   ```

3. **Download the dictionary data:**

   ```bash
   python -m unidic download
   ```
Note: This solution is likely to work, the same issue has been observed on both Colab and Hugging Face.





## License
[Kokoro model](https://huggingface.co/hexgrad/Kokoro-82M) is licensed under the [Apache License 2.0]
## Credits
[Kokoro HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M)
