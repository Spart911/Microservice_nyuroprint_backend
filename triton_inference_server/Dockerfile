# Используем официальное изображение Triton Inference Server
FROM nvcr.io/nvidia/tritonserver:25.02-py3

# Создаем рабочую директорию
WORKDIR /workspace

# Создаем структуру директорий для модели
RUN mkdir -p /workspace/model_repository/defect_detection_model/1


# Устанавливаем порты для Triton
# 8000 - HTTP, 8001 - gRPC, 8002 - metrics
EXPOSE 8000 8001 8002

# Запуск Triton Inference Server
CMD ["tritonserver", "--model-repository=/workspace/model_repository"]
