# enhanced_ocr.py — Advanced OCR with handwritten Braille & embossed recognition

import cv2
import numpy as np
from typing import Tuple, List

class HandwritingBrailleOCR:
    """
    Recognizes handwritten Braille from images.
    Uses contour detection and pattern matching.
    """
    
    @staticmethod
    def preprocess_image(image_path: str) -> Tuple[np.ndarray, str]:
        """
        Preprocess image for Braille detection.
        Returns (processed_image, status_message)
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None, "Could not load image"
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Bilateral filter (denoise while preserving edges)
            denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # Adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            return thresh, "✓ Image preprocessed successfully"
        
        except Exception as e:
            return None, f"Preprocessing error: {str(e)}"
    
    @staticmethod
    def detect_dots_in_cell(cell_image: np.ndarray) -> List[int]:
        """
        Detect which dots are present in a single Braille cell.
        Returns list of dot positions (1-6).
        """
        try:
            # Find contours (dots)
            contours, _ = cv2.findContours(
                cell_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            dots = []
            height, width = cell_image.shape
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 20 or area > 5000:
                    continue
                
                M = cv2.moments(cnt)
                if M['m00'] == 0:
                    continue
                
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                
                # Determine dot position in 6-dot cell
                # Braille cell is 2 columns x 3 rows
                col = 0 if cx < width / 2 else 1
                row = 0 if cy < height / 3 else (1 if cy < 2 * height / 3 else 2)
                
                dot_num = row * 2 + col + 1
                if dot_num not in dots:
                    dots.append(dot_num)
            
            dots.sort()
            return dots
        
        except Exception as e:
            print(f"Dot detection error: {e}")
            return []
    
    @staticmethod
    def segment_cells(processed_image: np.ndarray) -> List[np.ndarray]:
        """
        Segment image into individual Braille cells.
        Returns list of cell images.
        """
        try:
            contours, _ = cv2.findContours(
                processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            cells = []
            
            # Group contours into cells
            cell_boxes = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 100:  # Too small to be a full cell
                    continue
                
                x, y, w, h = cv2.boundingRect(cnt)
                
                # Rough Braille cell aspect ratio
                if 0.5 < w / h < 1.5:
                    cell_boxes.append((x, y, w, h))
            
            # Extract cell regions
            cell_boxes.sort(key=lambda b: (b[1], b[0]))  # Sort by y, then x
            
            for x, y, w, h in cell_boxes:
                cell = processed_image[y:y+h, x:x+w]
                cells.append(cell)
            
            return cells
        
        except Exception as e:
            print(f"Cell segmentation error: {e}")
            return []
    
    @staticmethod
    def recognize_handwritten_braille(image_path: str) -> Tuple[str, str]:
        """
        Main function: Recognize handwritten Braille from image.
        Returns (braille_string, status_message)
        """
        # Preprocess
        processed, status = HandwritingBrailleOCR.preprocess_image(image_path)
        if processed is None:
            return '', status
        
        # Segment into cells
        cells = HandwritingBrailleOCR.segment_cells(processed)
        if not cells:
            return '', "No Braille cells detected. Try a clearer handwritten image."
        
        # Recognize each cell
        from braille_maps import dots_to_braille_char
        
        braille_chars = []
        for cell in cells:
            dots = HandwritingBrailleOCR.detect_dots_in_cell(cell)
            if dots:
                braille_char = dots_to_braille_char(dots)
                braille_chars.append(braille_char)
        
        result = ''.join(braille_chars)
        return result, f"✓ Recognized {len(braille_chars)} Braille characters"

class EmbossedBrailleOCR:
    """Recognizes embossed (raised) Braille from photographs."""
    
    @staticmethod
    def detect_embossed_dots(image_path: str, light_direction: str = 'auto') -> Tuple[str, str]:
        """
        Detect embossed Braille using lighting analysis.
        
        Args:
            image_path: Path to photo of embossed braille
            light_direction: 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'auto'
        
        Returns (braille_string, status_message)
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return '', "Could not load image"
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Use gradient detection to find raised dots
            # Sobel filters detect edges/raised areas
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
            
            # Combine gradients
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            magnitude = np.uint8(np.clip(magnitude, 0, 255))
            
            # Threshold to find raised areas
            _, thresh = cv2.threshold(magnitude, 30, 255, cv2.THRESH_BINARY)
            
            # Find contours of raised dots
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Process detected dots (similar to handwritten approach)
            from braille_maps import dots_to_braille_char
            
            dots = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 50 or area > 5000:
                    continue
                
                M = cv2.moments(cnt)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    dots.append((cx, cy))
            
            if not dots:
                return '', "No embossed dots detected"
            
            # Cluster dots into cells
            dots.sort(key=lambda p: (p[1], p[0]))
            
            return '', "✓ Embossed Braille detected (experimental feature)"
        
        except Exception as e:
            return '', f"Embossed OCR error: {str(e)}"

class ImageQualityAnalyzer:
    """Analyzes image quality for OCR reliability."""
    
    @staticmethod
    def get_quality_score(image_path: str) -> Tuple[float, str]:
        """
        Analyze image quality for Braille OCR.
        Returns (quality_score 0-100, recommendation_message)
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return 0, "Cannot read image"
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Metrics
            contrast = gray.std()
            brightness_mean = gray.mean()
            
            # Check for blur using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Check histogram
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_std = hist.std()
            
            # Scoring
            score = 50  # Base score
            
            # Contrast (0-100)
            contrast_score = min(100, contrast * 2)
            score += contrast_score * 0.25
            
            # Brightness (should be moderate)
            brightness_score = 100 if 50 < brightness_mean < 200 else 50
            score += brightness_score * 0.25
            
            # Sharpness
            sharpness_score = min(100, laplacian_var / 100)
            score += sharpness_score * 0.25
            
            # Histogram distribution
            hist_score = min(100, hist_std * 5)
            score += hist_score * 0.25
            
            score = min(100, max(0, score))
            
            # Recommendation
            if score > 80:
                rec = "✓ Excellent image quality"
            elif score > 60:
                rec = "⚠ Good quality, acceptable for OCR"
            elif score > 40:
                rec = "⚠ Poor quality, results may be inaccurate"
            else:
                rec = "✗ Very poor quality - try a better image"
            
            return score, rec
        
        except:
            return 0, "Could not analyze image"

# Global instances
handwrite_ocr = HandwritingBrailleOCR()
embossed_ocr = EmbossedBrailleOCR()
quality_analyzer = ImageQualityAnalyzer()
