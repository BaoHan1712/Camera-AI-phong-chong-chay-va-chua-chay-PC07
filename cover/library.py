from flask import Flask, Response, render_template, jsonify, request
import cv2
from ultralytics import YOLO
import threading
from queue import Queue
import time
import os
from datetime import datetime
import boto3

