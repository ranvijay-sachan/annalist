# update test data in devel directory.  Data in sampledata/init is removed and regenerated
# 
# BASEDIR=/Users/graham/workspace/github/gklyne/annalist/src/annalist_root

# See: http://stackoverflow.com/questions/59895/
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "rm -rf $BASEDIR/sampledata/init/annalist_site/c" 
rm -rf $BASEDIR/sampledata/init/annalist_site/c

echo "rm -rf $BASEDIR/sampledata/data/annalist_site/c" 
rm -rf $BASEDIR/sampledata/data/annalist_site/c

python manage.py test \
    annalist.tests.test_createsitedata.CreateSiteData.test_CreateDevelSiteData

echo "rm -rf $BASEDIR/devel/annalist_site_backup"
rm -rf $BASEDIR/devel/annalist_site_backup

echo "mv $BASEDIR/devel/annalist_site $BASEDIR/devel/annalist_site_backup"
mv $BASEDIR/devel/annalist_site $BASEDIR/devel/annalist_site_backup

echo "cp -r $BASEDIR/sampledata/data/annalist_site $BASEDIR/devel/"
cp -r $BASEDIR/sampledata/data/annalist_site $BASEDIR/devel/

# Recreate initial test data
source makeinitsitedata.sh

# End.
