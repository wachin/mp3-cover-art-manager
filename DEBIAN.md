# Debian Packaging Guide

This document describes how to build and maintain the Debian package for MP3 Cover Art Manager.

## Building the Debian Package

### Prerequisites

You need a Debian-based system (Debian, Ubuntu, etc.) with the following packages installed:

```bash
sudo apt-get update
sudo apt-get install build-essential debhelper dh-python python3 python3-setuptools python3-pyqt6 python3-requests python3-mutagen pyqt6-dev-tools
```

### Building the Package

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/mp3-cover-art-manager.git
   cd mp3-cover-art-manager
   ```

2. **Build the source package:**
   ```bash
   dpkg-buildpackage -us -uc
   ```

   This will create:
   - `mp3-cover-art-manager_1.0.0-1.dsc` - Source package description
   - `mp3-cover-art-manager_1.0.0-1.tar.xz` - Source tarball
   - `mp3-cover-art-manager_1.0.0-1_amd64.deb` - Binary package (on amd64)

3. **Install the package:**
   ```bash
   sudo dpkg -i ../mp3-cover-art-manager_1.0.0-1_amd64.deb
   ```

4. **Run the application:**
   ```bash
   mp3-cover-art-manager
   ```
   Or from the application menu.

## Maintaining the Package

### Updating the Changelog

When making changes to the package, update the changelog:

```bash
dch -i
```

This will open the changelog in your default editor. Follow the Debian changelog format.

### Building for Different Architectures

To build for a specific architecture:

```bash
dpkg-buildpackage -aarm64 -us -uc
```

### Building Source Package Only

To build only the source package (no binary):

```bash
dpkg-buildpackage -S -us -uc
```

### Using pbuilder for Clean Builds

For reproducible builds in a clean environment:

1. **Install pbuilder:**
   ```bash
   sudo apt-get install pbuilder
   ```

2. **Create a pbuilder chroot:**
   ```bash   sudo pbuilder create
   ```

3. **Build the package:**
   ```bash
   pdebuild
   ```

## Debian Policy Compliance

This package follows Debian Policy Manual version 4.6.2 and uses:
- debhelper-compat 13
- Python packaging with pybuild
- Standard filesystem hierarchy

### Package Structure

```
/usr/bin/cover_finder.py              - Main executable
/usr/share/pixmaps/cover_finder.svg   - Application icon
/usr/share/applications/mp3-cover-art-manager.desktop - Desktop entry
/usr/share/mp3-cover-art-manager/     - Translation files
/usr/share/doc/mp3-cover-art-manager/ - Documentation
```

## Submitting to Debian

To submit this package to the Debian repositories:

1. **Ensure all Debian policies are met:**
   - Check with `lintian`:
     ```bash
     lintian ../mp3-cover-art-manager_1.0.0-1_amd64.deb
     ```
   - Fix any warnings or errors

2. **Get the package sponsored:**
   - Since you're not a Debian Developer yet, you need a sponsor
   - Post to the debian-mentors mailing list
   - Or find a sponsor through the Debian Packaging Team

3. **Upload via mentors.debian.net:**
   - Upload your source package to mentors.debian.net
   - Wait for a sponsor to review and upload to Debian

## GitHub Actions for Cross-Platform Builds

The `.github/workflows/build.yml` workflow automatically builds executables for:
- Linux (tar.gz)
- Windows (zip)
- macOS (tar.gz)

### Triggering Builds

Builds are triggered by:
- Pushing a tag starting with `v` (e.g., `v1.0.0`)
- Manual trigger via GitHub Actions UI

### Build Artifacts

The workflow creates:
- Standalone executables built with PyInstaller
- Archives containing the executable and translation files
- GitHub releases with the artifacts

### Local Testing

To test the build locally:

```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller cover_finder.spec

# The executable will be in dist/
```

## Translation Updates

When updating translations:

1. Update the `.ts` files with Qt Linguist
2. Compile to `.qm` files:
   ```bash
   lrelease cover_art_en.ts cover_art_es.ts
   ```
3. Rebuild the package to include updated translations

## Additional Resources

- [Debian Policy Manual](https://www.debian.org/doc/debian-policy/)
- [Debian Developer's Reference](https://www.debian.org/doc/manuals/developers-reference/)
- [Python Packaging in Debian](https://wiki.debian.org/Python/Packaging)
- [Debian Mentors](https://mentors.debian.net/)
