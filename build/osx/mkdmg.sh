commit=$(git log --format=format:%h HEAD~..HEAD)
date=$(date +%d%m%y)
rm -rf Kano_Burner
mkdir Kano_Burner
mv "./app/Kano Burner/Kano Burner.app" Kano_Burner
hdiutil create "./app/Kano Burner/Kano Burner OSx v2 rc${date} ${commit}.dmg" -srcfolder Kano_Burner -ov


