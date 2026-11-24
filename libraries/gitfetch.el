// ============================================================
//  gitfetch.el — GitHub File Downloader
//
//  A command library that adds Fetch() and InDIR() commands.
//
//  Usage in .ez scripts:
//    import gitfetch.el
//    Fetch("https://github.com/{user}/{repo}/{path}") InDIR("./downloads/")
// ============================================================

Def {
  Library.name: "GitFetch"
  Library.version: v1.0
  Package.identifier: "project1.ezcode.gitfetch"
}

// ── Fetch command ──────────────────────────────────────────
// Downloads a file from a URL to a specified directory.
//
// Usage:
//   Fetch("https://github.com/user/repo/file.txt") InDIR("./downloads/")
//
// The file is saved as ./downloads/file.txt

Cmd {
  Syntax: 'Fetch("{url}") InDIR("{path}")'
  Func: '
import os, urllib.request

# Extract filename from URL
filename = url.split("/")[-1] if "/" in url else "download"
save_dir = path
os.makedirs(save_dir, exist_ok=True)
save_path = os.path.join(save_dir, filename)

print("Downloading: " + url)
print("Saving to:   " + save_path)

try:
    urllib.request.urlretrieve(url, save_path)
    print("Download complete!")
except Exception as e:
    print("Download failed: " + str(e))
'
}

// ── FetchRaw command (no InDIR needed — saves to current dir) ──
Cmd {
  Syntax: 'FetchRaw("{url}")'
  Func: '
import os, urllib.request

filename = url.split("/")[-1] if "/" in url else "download"
save_path = os.path.join(".", filename)

print("Downloading: " + url)
print("Saving to:   " + save_path)

try:
    urllib.request.urlretrieve(url, save_path)
    print("Download complete!")
except Exception as e:
    print("Download failed: " + str(e))
'
}
