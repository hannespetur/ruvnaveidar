## Rúvnaveiðar

Rúvnaveiðar is a minimalist downloader for RÚV VODs for Linux, Mac and Windows. It is a faster version of [RÚV Sarpur](https://github.com/sverrirs/ruvsarpur) but has much more limited set of features and customization. Consider using Rúvsarpur if you need additional functionality.

### Install

Download the Github ZIP file or clone the repository

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

2. (optional) Run `ruvnaveidar` to list the all the episodes found.

```sh
$ python ruvnaveidar
```

3. If you want to fetch these episodes, run

```sh
$ python ruvnaveidar --run
```

After downloading with streamlink the episodes you have will be added to `blacklist.txt`, which will ignore those episodes in future runs.

### License

MIT
