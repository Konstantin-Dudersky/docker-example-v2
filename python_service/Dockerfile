FROM base_image
# контекст - родительская папка
COPY . /root/code 
WORKDIR /root/code/python_service
RUN poetry install --only main
# CMD ["poetry", "run", "start"]
CMD ["tail", "-f", "/dev/null"]
EXPOSE 8000
