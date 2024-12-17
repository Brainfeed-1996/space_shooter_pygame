import pygame
import numpy as np
from scipy.io import wavfile
import os

def create_retro_sound(frequency, duration, volume=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave = np.sin(2 * np.pi * frequency * t)
    fade = np.linspace(1, 0, len(wave))
    wave = wave * fade * volume
    
    sound_array = np.array([wave, wave]).T.copy()
    sound_array = (sound_array * 32767).astype(np.int16)
    
    return sound_array, sample_rate

def generate_sounds():
    # Laser sound
    laser_array, sample_rate = create_retro_sound(880, 0.1)
    laser_path = os.path.join('sounds', 'laser.wav')
    wavfile.write(laser_path, sample_rate, laser_array)
    
    # Explosion sound
    explosion_array, sample_rate = create_retro_sound(220, 0.3)
    explosion_path = os.path.join('sounds', 'explosion.wav')
    wavfile.write(explosion_path, sample_rate, explosion_array)
    
    # Powerup sound
    powerup_array, sample_rate = create_retro_sound(660, 0.2)
    powerup_path = os.path.join('sounds', 'powerup.wav')
    wavfile.write(powerup_path, sample_rate, powerup_array)
    
    # Background music (simple loop)
    music_duration = 5.0
    t = np.linspace(0, music_duration, int(44100 * music_duration))
    
    bass = np.sin(2 * np.pi * 55 * t) * 0.3
    melody = np.sin(2 * np.pi * 220 * t) * 0.2
    harmony = np.sin(2 * np.pi * 330 * t) * 0.1
    
    music = bass + melody + harmony
    music_array = np.array([music, music]).T.copy()
    music_array = (music_array * 32767).astype(np.int16)
    
    music_path = os.path.join('sounds', 'background.wav')
    wavfile.write(music_path, 44100, music_array)

if __name__ == "__main__":
    generate_sounds()
