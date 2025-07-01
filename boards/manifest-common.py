include("$(PORT_DIR)/boards/manifest.py")

# Handy for dealing with APIs
require("datetime")

# Add $CI_BUILD_DIR/version.py built by ci/micropython.sh:ci_genversion
freeze("$(PORT_DIR)/../../../", "version.py")

freeze("../modules/")
