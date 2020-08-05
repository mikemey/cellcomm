## Single-cell RNA-seq clustering/classification

### Part 1: ML encoding run

#### Requirements:

- Python 3, Keras/TensorFlow, MongoDB
```bash
[project-dir] $ pip3 install -r requirements.txt
```

#### Run:

```bash
[project-dir] $ python3 src
```


### Part 2: Celltype analysis service

#### Requirements:

- Node.js, MongoDB
```bash
[project-dir]/cellan $ npm install 
```

#### Start server:
```bash
[project-dir]/cellan $ npm start
```

