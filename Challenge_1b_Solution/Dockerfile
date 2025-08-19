# Base Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy files into container
COPY . .


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('models/all-MiniLM-L6-v2')"

# Set default command to run script
CMD ["bash", "run.sh"]
