commit=$(git log --format=format:%h HEAD~..HEAD)
mkdir dmgdir
mv "./app/Kano Burner/Kano Burner.app" dmgdir
hdiutil create "./app/Kano Burner/Kano Burner OSx v2 rc280415 ${commit}.dmg" -srcfolder dmgdir -ov 

