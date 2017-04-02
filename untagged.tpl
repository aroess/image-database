<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="cache-control" content="no-cache">

<link rel="stylesheet" href="../static/resources/bootstrap.3-3-6.min.css">
<title>Untagged Files</title>
</head>
<body>
<!--- HEADER ---->
<div id="header" name="top">
  <ul class="nav nav-tabs" role="navigation">
    <li role="presentation"><a href="/">Search</a></li>
    <li role="presentation"><a href="/edittags">Edit Tags</a></li>
    <li role="presentation" class="active"><a href="/untagged">Untagged Files</a></li>
    <li role="presentation"><a href="/tagcount">Count Tags</a></li>
    <li role="presentation"><a href="/refresh">Refresh Image Folder</a></li>
  </ul>
</div>
<!--- HEADER END ---->

<div style="width:450px; margin-left:20px;">
<h1>Untagged Files</h1>
<div class="list-group">
%for filepath, fileID in untaggedFiles:
    <a class="list-group-item" href="/edit/{{fileID}}">{{filepath}}</a>
%end
</div>
</div>
</body>
</html>
