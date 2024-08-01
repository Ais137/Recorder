FROM python:3.8-slim

COPY . /code/
COPY ./requirements.txt .

WORKDIR /code/

RUN pip install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["scrapy", "crawl", "BBSCollector-scrapy-redis"]
