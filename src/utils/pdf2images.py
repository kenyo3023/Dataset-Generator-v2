import pdf2image
import shutil
from pathlib import Path
from PIL import Image
from typing import List, Union


class PDF2ImagesConverter:
    """PDF to Image converter class with a transformers-like API style"""
    
    def __init__(self, images: List[Image.Image], source_path: Path):
        """
        Initialize the converter with converted images
        
        Args:
            images: List of converted PDF images
            source_path: Original PDF file path
        """
        self.images = images
        self.source_path = source_path
    
    @classmethod
    def convert_from(cls, file_path: Union[str, Path], **kwargs):
        """
        Create a converter instance from a PDF file, similar to transformers' from_pretrained
        
        Args:
            file_path: Path to the PDF file
            **kwargs: Additional arguments to pass to pdf2image.convert_from_path
            
        Returns:
            PDF2ImagesConverter: A new converter instance
            
        Raises:
            FileNotFoundError: When file doesn't exist
            ValueError: When file is not a PDF
        """
        # Convert to Path object for better handling
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Validate file format
        if file_path.suffix.lower() != '.pdf':
            raise ValueError(f"File must be PDF format: {file_path}")
            
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(str(file_path), **kwargs)
            return cls(images=images, source_path=file_path)
        except Exception as e:
            raise RuntimeError(f"Error converting PDF: {str(e)}")
    
    def save(self, 
             save_directory: Union[str, Path] = None, 
             format: str = 'JPEG',
             quality: int = 95,
             clean_dir: bool = True,
             **kwargs) -> int:
        """
        Save converted images to specified directory
        
        Args:
            save_directory: Directory path to save images. If None, uses PDF filename as directory
            format: Image format, defaults to 'JPEG'
            quality: Image quality (1-100), defaults to 95
            clean_dir: Whether to clean the directory before saving. If True, deletes all existing 
                      content in the directory. Defaults to True
            **kwargs: Additional arguments to pass to image.save()

        Raises:
            RuntimeError: When saving process fails
        """
        try:
            # Use PDF filename if no save directory specified
            if save_directory is None:
                save_directory = self.source_path.with_suffix('')
            else:
                save_directory = Path(save_directory)

            # Handle directory cleaning if requested
            if clean_dir and save_directory.exists():
                shutil.rmtree(save_directory)
                save_directory.mkdir(parents=True)
            elif not save_directory.exists():
                save_directory.mkdir(parents=True)
            
            # Save all images
            for i, image in enumerate(self.images):
                output_file = save_directory / f'page_{i+1}.{format.lower()}'
                image.save(
                    str(output_file),
                    format,
                    quality=quality,
                    optimize=True,
                    **kwargs
                )
        except Exception as e:
            raise RuntimeError(f"Error saving images: {str(e)}")

    def __len__(self) -> int:
        """Return the number of converted images"""
        return len(self.images)

    def __getitem__(self, index: int) -> Image.Image:
        """Support indexing to access converted images"""
        return self.images[index]