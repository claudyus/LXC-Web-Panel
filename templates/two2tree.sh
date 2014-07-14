#/bin/bash

#from http://upgrade-bootstrap.bootply.com/
if [[ -z $1 ]]; then
	echo "Usage: $0 filename"
	exit 1
fi

sed -i 's/container-fluid/container/g' $1
sed -i 's/row-fluid/row/g' $1
sed -i 's/\(class=.*\)span/\1col-md-/g' $1
sed -i 's/offset/col-md-offset-/g' $1
sed -i 's/brand/navbar-brand/g' $1
sed -i 's/navbar nav/nav navbar-nav/g' $1
sed -i 's/hero-unit/jumbotron/g' $1
sed -i 's/\(class=.*\)icon-/\1glyphicon glyphicon-/g' $1
sed -i 's/btn/btn btn-default/g' $1
sed -i 's/btn-mini/btn-xs/g' $1
sed -i 's/btn-small/btn-sm/g' $1
sed -i 's/btn-large/btn-lg/g' $1
sed -i 's/visible-phone/visible-sm/g' $1
sed -i 's/visible-tablet/visible-md/g' $1
sed -i 's/visible-desktop/visible-lg/g' $1
sed -i 's/hidden-phone/hidden-sm/g' $1
sed -i 's/hidden-tablet/hidden-md/g' $1
sed -i 's/hidden-desktop/hidden-lg/g' $1
sed -i 's/input-prepend/input-group/g' $1
sed -i 's/input-append/input-group/g' $1
sed -i 's/add-on/input-group-addon/g' $1
sed -i 's/btn-navbar/navbar-btn/g' $1
sed -i 's/thumbnail/img-thumbnail/g' $1
