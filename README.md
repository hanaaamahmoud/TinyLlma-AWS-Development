# End-to-End Fine-Tuning & Deployment of TinyLlama on AWS

This project demonstrates a complete AI lifecycle: from data processing using PySpark on EMR to fine-tuning a TinyLlama model and deploying it on an AWS EC2 instance with a web-based UI using Ollama and Open WebUI.

---

## Prerequisites

- **AWS Account** (with access to EC2, EMR, S3, IAM)
- **Region:** `us-east-1` (N. Virginia)
- **Tools installed locally:** Git, AWS CLI, and an SSH client
- **Hardware for fine-tuning:** Google Colab (T4 GPU) or local GPU

---

##  Step-by-Step Replication Guide

### Phase 1: Data Processing with PySpark on EMR

1. Upload the raw dataset (WebFAQ English subset, 21M records) to an S3 bucket:  
   `s3://20596371-chatbot-data/raw/`
2. Launch an EMR cluster (1 master + 1 core, `m5.xlarge`) in `us-east-1`.
3. Run the PySpark preprocessing script:  
   [`data_processing/data_preprocessing.py`](data_processing/data_preprocessing.py)
4. The script cleans the data, splits into train/val/test (80/10/10), and saves output to:  
   `s3://20596371-chatbot-data/processed/`
5. **Terminate the EMR cluster** after the job finishes.

---

### Phase 2: Fine-Tuning TinyLlama with QLoRA

1. Open the fine-tuning notebook:  
   [`notebooks/tinyllama_finetuning.ipynb`](notebooks/tinyllama_finetuning.ipynb)
2. Run it in **Google Colab** with GPU enabled (T4 or A100).
3. The notebook uses **Unsloth + QLoRA** (4-bit quantization, LoRA rank=16).
4. Training hyperparameters:
   - Learning rate: 2e-4
   - Batch size: 2 (effective 8 with gradient accumulation)
   - Epochs: 3 (or 300 steps for sample file)
5. After training, the notebook exports the model to **GGUF format** (`model.gguf`).

---

### Phase 3: AWS Infrastructure (VPC & EC2)

- A custom VPC was created: `20596371-project-vpc` (CIDR `10.0.0.0/16`)
- Public subnet: `10.0.1.0/24`, Private subnet: `10.0.2.0/24`
- Internet Gateway attached, route table configured for public subnet
- Security group allows:
  - SSH (port 22) from my IP only
  - HTTP (port 80) for Open WebUI
  - Custom TCP (port 11434) for Ollama API

---

### Phase 4: Model Deployment on EC2 with Ollama

1. Launch an EC2 instance (Ubuntu 22.04, `t3.medium`, 20GB EBS) in the public subnet.
2. Copy the fine-tuned `model.gguf` to the instance:
   ```bash
   scp -i your-key.pem model.gguf ubuntu@<EC2_PUBLIC_IP>:/home/ubuntu/
   ```
3. Install Ollama on EC2:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
4. Create a `Modelfile` (provided in the root of this repo) and build the model:
   ```bash
   ollama create my-finetuned-model -f Modelfile
   ```
5. Serve the model:
   ```bash
   ollama serve &
   ```
6. Test with curl:
   ```bash
   curl http://localhost:11434/api/generate -d '{"model": "my-finetuned-model", "prompt": "What are houses in Africa called?"}'
   ```

---

### Phase 5: Web Interface with Open WebUI

1. Install Docker on the EC2 instance:
   ```bash
   sudo apt update && sudo apt install docker.io -y
   ```
2. Run Open WebUI container (auto-restart enabled):
   ```bash
   sudo docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway --name webui --restart always ghcr.io/open-webui/open-webui:main
   ```
3. Access the chat interface in your browser:
   ```
   http://<EC2_PUBLIC_IP>:3000
   ```
4. Select the model `my-finetuned-model` and start chatting.

---

##  Cost Summary Table (Approximate AWS Spend)

| Service | Instance/Type | Duration | Cost (USD) |
|---------|---------------|----------|-------------|
| S3 Storage | 20 GB (raw+processed+models) | 1 month | ~$0.50 |
| EMR (preprocessing) | 2 × m5.xlarge | 2 hours | ~$0.96 |
| EC2 (fine-tuning – optional, used Colab free) | – | – | $0.00 |
| EC2 (deployment) | t3.medium | 10 hours | ~$0.40 |
| **Total** | – | – | **~$1.86** |

> *All costs are estimates using on-demand us-east-1 pricing. Actual costs may vary.*

---

## 📎 Repository Structure
TinyLlama-AWS-Deployment/
├── data_processing/
│ ├── data_ingestion.py
│ └── data_preprocessing.py
├── notebooks/
│ └── tinyllama_finetuning.ipynb
├── Modelfile
├── README.md
└── .gitignore




