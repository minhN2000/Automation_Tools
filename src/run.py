import os
from AutoPrinting import AutoPrinting

autoPrinting = AutoPrinting("")


yourAndroidAppDirHere = 'C:/Users/Minh/Downloads/loyalty-card-locker-db3d93e1bc6e056e7288260d042c646ff17b0c13\loyalty-card-locker-db3d93e1bc6e056e7288260d042c646ff17b0c13/app/src/main/java/protect/card_locker/'

# Loop through the Android apps and add print statments for all .java files
for root, dirs, files in os.walk(yourAndroidAppDirHere):
    for file in files:
        print(file)
        autoPrinting.setNewName(os.path.join(root, file))
        autoPrinting.main()
