## Rúvnaveiðar

Rúvnaveiðar is a minimalist version of [https://github.com/sverrirs/ruvsarpur](RÚV Sarpur).

### Install

Clone the repository

```sh
git clone https://github.com/hannespetur/ruvnaveidar
cd ruvnaveidar
```

Install dependencies

```sh
pip install -r requirements.txt
```

### Usage

Add shows you would like to fetch from Rúv in a file named `whitelist.txt` (one show per line). Running the script will download all shows found

```sh
./ruvnaveidar.py
```

After downloading with streamlink the episodes you have will be added to `blacklist.txt`, which will ignore those episodes in future runs.

### License

MIT