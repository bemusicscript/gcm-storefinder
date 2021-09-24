# gcm-storefinder

https://location.am-all.net からデータをクローリングして地図を作りました。

全ての機器が一緒に設置されているゲーセン地図がないので作りました。

# DEMO

https://bemusicscript.github.io/gcm-storefinder/

# Crawler Update & Push

```sh

$ python3 storemap.py
$ git add ./json/
$ git commit -m "JSON Update $(date '+%Y-%m-%d %H:%M:%S')"
$ git push origin master
```
