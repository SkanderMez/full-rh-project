FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip 
#RUN pip install -U scikit-learn scipy sklearn-crfsuite 
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt 
EXPOSE 2999 
ENTRYPOINT [ "python" ] 
CMD [ "app.py" ]
