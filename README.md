# Persona-Driven Document Intelligence

---

## 🔗 Docker Hub

You can pull and run the image directly from Docker Hub:

➡️ [adityapatil7730/1b on Docker Hub](https://hub.docker.com/repository/docker/adityapatil7730/1b/general)

---

This project provides a practical, persona-focused approach to extracting meaningful, actionable content from PDF documents. It is especially useful for professionals seeking to surface only the most relevant sections from large documentation sets, tailored to their specific job and role.

---

## 🧠 Methodology

The system combines natural language processing (NLP) with semantic similarity to identify the most valuable insights based on the user's persona and job objective.

### 🔍 Core Processing Pipeline

**1. Text Extraction & Cleaning**

* Processes PDFs in overlapping 2-page windows to preserve context.
* Normalizes Unicode and removes special/control characters.
* Cleans up excessive whitespace.

**2. Semantic Understanding**

* Uses spaCy's `en_core_web_md` model to compute semantic embeddings.
* Measures cosine similarity between PDF chunks and a job/persona prompt.

**3. Hybrid Scoring System**

* **Semantic Similarity (80%)**: Measures conceptual match to the job context.
* **Keyword Relevance (10%)**: Scores presence of critical context keywords.
* **Actionable Intent (10%)**: Detects actionable verbs (e.g., "implement," "optimize").

**4. Multi-Stage Filtering**

* Selects top 2 relevant sections from each document.
* Ranks globally to extract the 5 most valuable insights.
* Includes metadata such as document name and page number.

---

## 🚀 Key Innovations

### Contextual Chunking

* Maintains narrative integrity by processing overlapping pages.

### Intelligent Normalization

* Preserves semantically important symbols while cleaning the text.

### Action-Oriented Filtering

* Highlights insights with verbs indicating action or recommendations.

### Role-Specific Weighting

* Tailors output by comparing content to both the persona and job description.

---

## 🐳 Docker Implementation

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install -r requirements.txt

RUN mkdir -p documents output

CMD ["python", "main.py"]
```

### requirements.txt

```text
fitz==0.0.1.dev2
pymupdf==1.24.3
spacy==3.7.4
numpy==1.26.4
unicodedata2==15.1.0
```

---

## 🛠️ How to Run

### Step 1: Build the Docker Image

```bash
docker build --platform linux/amd64 -t adityapatil7730/1b .
```

### Step 2: Prepare Folders

```bash
mkdir -p documents output
```

### Step 3: Add PDF Documents

```bash
cp /path/to/your/pdfs/*.pdf documents/
```

### Step 4: Run the Container

```bash
docker run -it   -e PERSONA="Financial Analyst"   -e JOB="Evaluate Q3 earnings report"   -v ./documents:/app/documents   -v ./output:/app/output   1b
```

### Example

```bash
docker run -it   -e PERSONA="Financial Analyst"   -e JOB="Evaluate Q3 earnings report"   -v ./documents:/app/documents   -v ./output:/app/output   1b
```

---

## 📦 Output

The output will appear in the `output/` directory as JSON files.

### Sample Output Structure

```json
{
  "metadata": {
    "input_documents": ["report.pdf"],
    "persona": "Financial Analyst",
    "job_to_be_done": "Evaluate Q3 earnings report",
    "processing_timestamp": "2023-11-15T14:30:45.123456"
  },
  "extracted_sections": [
    {
      "document": "report.pdf",
      "section_title": "Q3 Financial Highlights: Revenue growth of 15%...",
      "importance_rank": 1,
      "page_number": 5
    }
  ],
  "subsection_analysis": [
    {
      "document": "report.pdf",
      "refined_text": "Q3 Financial Highlights: Revenue growth of 15% year-over-year...",
      "page_number": 5
    }
  ]
}
```

---

## 📂 Volume Mounts

| Path on Host | Path in Container | Purpose           |
| ------------ | ----------------- | ----------------- |
| `documents/` | `/app/documents`  | Input PDFs        |
| `output/`    | `/app/output`     | JSON output files |

> ✅ *It's recommended to mount the `documents/` folder as read-only:*

```bash
-v $(pwd)/documents:/app/documents:ro
```

---

## 🔐 Security Best Practices

* Use `--network none` to prevent network access
* Mount input folder as read-only
* Use `--userns=host` to isolate user permissions
* Set memory limits with `--memory 2g`
* Use temporary storage with `--tmpfs /tmp:rw,size=1g`


