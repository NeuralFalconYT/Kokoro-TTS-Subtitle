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



---

4. **Install eSpeak NG**

- **For Windows:**
  1. Download the latest eSpeak NG release from the [eSpeak NG GitHub Releases](https://github.com/espeak-ng/espeak-ng/releases/tag/1.51).
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
     python app.py
     ```
   Or,<br>
   ```
   python one_clicker.py
   ```
   Then, double-click on `run_app.bat` (Windows) to execute the script.



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
##### To clear the HuggingFace cache models:
   - Navigate to `C:\Users\<username>\.cache\huggingface\hub`
   - Delete the contents of the `hub` folder.
That's it! You've successfully removed everything.



## License
[Kokoro model](https://huggingface.co/hexgrad/Kokoro-82M) is licensed under the [Apache License 2.0]
## Credits
[Kokoro HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M)
