<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="cache-control" content="no-cache">


<script type="text/javascript" src="http://code.jquery.com/jquery-latest.min.js"></script>
<script type="text/javascript" src="../static/resources/bootstrap3-typeahead.min.js"></script>
<script type="text/javascript" src="../static/resources/edit_tags.js"></script>

<link rel="stylesheet" type="text/css" href="../static/resources/main.css">
<link rel="stylesheet" href="../static/resources/bootstrap.3-3-6.min.css">
<title>Add keywords</title>
</head>
<body>

<!--- HEADER ---->
<div id="header" name="top">
  <ul class="nav nav-tabs" role="navigation">
    <li role="presentation"><a href="/">Search</a></li>
    <li role="presentation" class="active"><a href="/edittags">Edit Tags</a></li>
    <li role="presentation"><a href="/untagged">Untagged Files</a></li>
    <li role="presentation"><a href="/tagcount">Count Tags</a></li>
    <li role="presentation"><a href="/refresh">Refresh Image Folder</a></li>
  </ul>
</div>
<!--- HEADER END ---->

<!--- SEARCHBAR ---->
<div class="input-group" id="searchBar">
  <input autofocus="autofocus" autocomplete="off" type="text" class="form-control typeahead" name="keyword" placeholder="Add tag to database..." aria-describedby="basic-addon1">
  <span class="input-group-btn">
    <button class="btn btn-default" type="button" id="button_add">Add</button>
  </span>
</div>
<!--- SEARCHBAR END ---->

<!--- TAGBAR ---->
<div id="tagBar"></div>
<!--- TAGBAR END ---->

<div id="tagbuttons">
%for entry in allTags:
    <input type=button  class="btn btn-primary btn-sm tagBarButton" value='{{entry}} ✖' name='{{entry}}' />
%end
</div>
</body></html>
