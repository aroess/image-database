# Image Database
A local-only web application for managing image tags.
### Dependencies ###
* Python 2.7.x
* imagemagick (for thumbnails)
* bottlepy 0.13-dev web framework (included)
* bootstrap 3.x css definitions (inlcuded)
* bootstrap 3-typeahead javascript library (included)
* jquery 1.x javascript library (included)

### Features ###
* SQlite database
* Responsive web interface
* View, edit, add, delete tags for image files
* View untagged files
* Count assigned tags

```
$ python server.py 
Bottle v0.13-dev server starting up (using WSGIRefServer())...
Listening on http://localhost:8080/
Hit Ctrl-C to quit.
```

### Screenshot ###
![screenshot](https://raw.githubusercontent.com/aroess/image-database/master/screenshot.png)
