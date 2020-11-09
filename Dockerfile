FROM python

WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
COPY install.txt .
RUN pip install -r install.txt

EXPOSE 3000
ENTRYPOINT [ "flask", "run", "--host=0.0.0.0", "--port=3000" ]

COPY . .