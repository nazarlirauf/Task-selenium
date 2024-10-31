FROM python:slim
WORKDIR /app
COPY test_script.py /app
RUN pip install selenium
RUN touch /app/output.log
RUN ln -sf /dev/stdout /app/output.log
CMD ["sh", "-c", "python test_script.py > output.log 2>&1"]
