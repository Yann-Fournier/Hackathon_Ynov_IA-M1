FROM ollama/ollama:latest

COPY rendu/infra/Modelfile /Modelfile

EXPOSE 11434

ENTRYPOINT ["/bin/sh", "-c", "\
    ollama serve & \
    until ollama list >/dev/null 2>&1; do sleep 1; done && \
    ollama create techcorp-finance -f /Modelfile && \
    wait"]