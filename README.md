## Rúvnaveiðar

Rúvnaveiðar is a minimalist version of [RÚV Sarpur](https://github.com/sverrirs/ruvsarpur). Consider using Rúvsarpur if you need additional functionality.

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

1. Create `whitelist.txt`

```sh
$ cat whitelist.template.txt
# Add shows you want to fetch from RÚV here, one per line
# i.e.:
Blæja
Friðþjófur forvitni
Hvolpasveitin
$ mv whitelist.template.txt whitelist.txt # For demonstration
```

2. Run `ruvnaveidar`

$ ./ruvnaveidar
```

After downloading with streamlink the episodes you have will be added to `blacklist.txt`, which will ignore those episodes in future runs.

### License

MIT