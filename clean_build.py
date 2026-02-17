#!/usr/bin/env python3
import os
import shutil
import subprocess

def clean_build():
    print("🧹 Cleaning...")
    for item in ['build', 'dist', '__pycache__', 'DeckReady.spec']:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg found")
            return True
    except:
        pass
    print("❌ FFmpeg not found - install with: brew install ffmpeg")
    return False

def build_app():
    print("🚀 Building DeckReady...")
    
    ffmpeg_path = shutil.which('ffmpeg')
    
    cmd = [
        'pyinstaller',
        '--onedir',
        '--windowed',
        '--name=DeckReady',
        '--icon=icon.ico',
        '--add-data=config:config',
        '--add-data=ui:ui', 
        '--add-data=core:core',
        '--clean',
        'app.py'
    ]
    
    if ffmpeg_path:
        cmd.insert(-1, f'--add-binary={ffmpeg_path}:.')
        print(f"📦 Including FFmpeg: {ffmpeg_path}")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ Build complete!")
        print("📁 Test: ./dist/DeckReady/DeckReady")
        print("🍎 Install: cp -R dist/DeckReady /Applications/")
        return True
    else:
        print("❌ Build failed!")
        return False

if __name__ == "__main__":
    if not check_ffmpeg():
        exit(1)
    clean_build()
    build_app()
