import streamlit as st
from PIL import Image
import json
import boto3
import tempfile

def compare_faces(sourceFile, targetFile):
    client = boto3.client('rekognition')

    imageSource = open(sourceFile, 'rb')
    imageTarget = open(targetFile, 'rb')

    response = client.compare_faces(SimilarityThreshold=80,
                                    SourceImage={'Bytes': imageSource.read()},
                                    TargetImage={'Bytes': imageTarget.read()})
    
    imageSource.close()
    imageTarget.close()
    return response

def convert_uploaded_file_to_temp_file(uploaded_file):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    file_content = uploaded_file.read()
    temp_file.write(file_content)
    uploaded_file.seek(0)  # Reset the read pointer to the start of the file
    return temp_file.name

def main():
    st.title("Google Photos Search")

    if 'source_image_file_paths' not in st.session_state:
        st.session_state.source_image_file_paths = []

    if 'matched_images' not in st.session_state:
        st.session_state.matched_images = []

    with st.sidebar:
        image_files = st.file_uploader("Upload source images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        submit = st.button("Submit")
        if submit and image_files:
            for image_file in image_files:
                st.session_state.source_image_file_paths.append(image_file)
            st.write("Images uploaded successfully")

    reference_img = st.file_uploader("Upload reference image", type=['png', 'jpg', 'jpeg'])
    if reference_img and st.button("Find Matches"):
        with st.spinner("Searching for matches"):
            st.session_state.matched_images = []
            for source_img in st.session_state.source_image_file_paths:
                st.write(f"Comparing {source_img.name} with {reference_img.name}")
                try:
                    response = compare_faces(convert_uploaded_file_to_temp_file(reference_img), convert_uploaded_file_to_temp_file(source_img))
                    if len(response['FaceMatches']) > 0:
                        st.write(f"Match found in {source_img.name}")
                        st.divider()
                        st.session_state.matched_images.append(source_img)
                    else:
                        st.write("No matches found")
                        st.divider()
                except Exception as e:
                    st.write(f"Error: {e}")    
        st.divider()
        if len(st.session_state.matched_images) == 0:
            st.write("Target person not found in any of the source images.")
        else:
            st.image(st.session_state.matched_images)


if __name__ == "__main__":
    main()
