import os
from AutoPrinting import AutoPrinting

autoPrinting = AutoPrinting("")


yourAndroidAppDirHere = 'C:/Users/Minh/Downloads/apps_Feb2/Omni-Notes - Copy/omniNotes/src/main/java/it/feio/android/omninotes'

# Loop through the Android apps and add print statments for all .java files
for root, dirs, files in os.walk(yourAndroidAppDirHere):
    for file in files:
        print(file)
        autoPrinting.setNewName(os.path.join(root, file))
        autoPrinting.main()
