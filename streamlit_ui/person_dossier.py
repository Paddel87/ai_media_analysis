import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
from PIL import Image
import io
import base64
import plotly.express as px
import plotly.graph_objects as go

# Konfiguration
API_BASE_URL = "http://localhost:8000"
DOOSSIER_SERVICE_URL = f"{API_BASE_URL}/dossiers"

def load_dossiers():
    """Lädt alle Dossiers vom Service"""
    response = requests.get(DOOSSIER_SERVICE_URL)
    if response.status_code == 200:
        return response.json()
    return []

def get_dossier(dossier_id):
    """Lädt ein spezifisches Dossier"""
    response = requests.get(f"{DOOSSIER_SERVICE_URL}/{dossier_id}")
    if response.status_code == 200:
        return response.json()
    return None

def update_dossier(dossier_id, updates):
    """Aktualisiert ein Dossier"""
    response = requests.put(f"{DOOSSIER_SERVICE_URL}/{dossier_id}", json=updates)
    return response.status_code == 200

def create_dossier(temporary_id):
    """Erstellt ein neues Dossier"""
    response = requests.post(DOOSSIER_SERVICE_URL, params={"temporary_id": temporary_id})
    return response.json() if response.status_code == 200 else None

def search_dossiers(query):
    """Sucht nach Dossiers"""
    response = requests.get(f"{DOOSSIER_SERVICE_URL}/search", params={"query": query})
    if response.status_code == 200:
        return response.json()
    return []

def display_face_image(face_instance):
    """Zeigt ein Gesichtsbild an"""
    if face_instance.get("image_url"):
        st.image(face_instance["image_url"], width=200)
    else:
        st.write("Kein Bild verfügbar")

def plot_emotion_stats(emotion_stats):
    """Erstellt ein Diagramm für die Emotionsstatistiken"""
    if not emotion_stats:
        return
    
    df = pd.DataFrame(list(emotion_stats.items()), columns=['Emotion', 'Häufigkeit'])
    fig = px.bar(df, x='Emotion', y='Häufigkeit', title='Emotionsverteilung')
    st.plotly_chart(fig)

def plot_restraint_stats(restraint_stats):
    """Erstellt ein Diagramm für die Restraint-Statistiken"""
    if not restraint_stats:
        return
    
    df = pd.DataFrame(list(restraint_stats.items()), columns=['Restraint', 'Häufigkeit'])
    fig = px.bar(df, x='Restraint', y='Häufigkeit', title='Restraint-Verteilung')
    st.plotly_chart(fig)

def display_media_appearances(appearances):
    """Zeigt die Medienauftritte an"""
    if not appearances:
        st.info("Keine Medienauftritte vorhanden")
        return
    
    for appearance in appearances:
        with st.expander(f"Medienauftritt: {appearance['media_id']} ({appearance['source_type']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"Job ID: {appearance['job_id']}")
                st.write(f"Zeitstempel: {datetime.fromisoformat(appearance['timestamp']).strftime('%Y-%m-%d %H:%M')}")
                if appearance.get('duration'):
                    st.write(f"Dauer: {appearance['duration']:.2f}s")
                if appearance.get('frame_number'):
                    st.write(f"Frame: {appearance['frame_number']}")
            
            with col2:
                if appearance.get('emotions'):
                    st.write("Emotionen:")
                    for emotion in appearance['emotions']:
                        for emotion_type, confidence in emotion.items():
                            st.write(f"- {emotion_type}: {confidence:.2f}")
                
                if appearance.get('restraints'):
                    st.write("Restraints:")
                    for restraint in appearance['restraints']:
                        for restraint_type, confidence in restraint.items():
                            st.write(f"- {restraint_type}: {confidence:.2f}")
            
            if appearance.get('context'):
                st.write("Kontext:", appearance['context'])
            if appearance.get('scene_description'):
                st.write("Szenenbeschreibung:", appearance['scene_description'])

def main():
    st.title("Personendossier-Verwaltung")
    
    # Sidebar für Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Seite auswählen", ["Übersicht", "Dossier bearbeiten", "Neues Dossier"])
    
    if page == "Übersicht":
        show_overview()
    elif page == "Dossier bearbeiten":
        show_dossier_editor()
    else:
        show_new_dossier()

def show_overview():
    """Zeigt die Übersicht aller Dossiers"""
    st.header("Dossier-Übersicht")
    
    # Suchleiste
    search_query = st.text_input("Suche nach Dossiers", "")
    if search_query:
        dossiers = search_dossiers(search_query)
    else:
        dossiers = load_dossiers()
    
    # Dossier-Tabelle
    if dossiers:
        df = pd.DataFrame([{
            "Temporäre ID": d["temporary_id"],
            "Anzeigename": d.get("display_name", ""),
            "Gesichter": len(d["face_instances"]),
            "Medienauftritte": len(d.get("media_appearances", [])),
            "Erstellt": datetime.fromisoformat(d["created_at"]).strftime("%Y-%m-%d %H:%M"),
            "Aktualisiert": datetime.fromisoformat(d["updated_at"]).strftime("%Y-%m-%d %H:%M")
        } for d in dossiers])
        st.dataframe(df)
    else:
        st.info("Keine Dossiers gefunden")

def show_dossier_editor():
    """Zeigt den Dossier-Editor"""
    st.header("Dossier bearbeiten")
    
    # Dossier auswählen
    dossiers = load_dossiers()
    if not dossiers:
        st.warning("Keine Dossiers verfügbar")
        return
    
    dossier_options = {f"{d['temporary_id']} ({d.get('display_name', 'Kein Name')})": d["dossier_id"] 
                      for d in dossiers}
    selected_dossier = st.selectbox("Dossier auswählen", list(dossier_options.keys()))
    dossier_id = dossier_options[selected_dossier]
    
    # Dossier laden
    dossier = get_dossier(dossier_id)
    if not dossier:
        st.error("Dossier konnte nicht geladen werden")
        return
    
    # Dossier bearbeiten
    with st.form("dossier_edit_form"):
        temporary_id = st.text_input("Temporäre ID", dossier["temporary_id"])
        display_name = st.text_input("Anzeigename", dossier.get("display_name", ""))
        notes = st.text_area("Notizen", dossier.get("notes", ""))
        
        # Metadaten
        st.subheader("Metadaten")
        metadata = dossier.get("metadata", {})
        new_metadata = {}
        for key, value in metadata.items():
            new_value = st.text_input(f"Metadata: {key}", value)
            if new_value != value:
                new_metadata[key] = new_value
        
        # Neues Metadatum hinzufügen
        new_key = st.text_input("Neues Metadatum (Schlüssel)")
        new_value = st.text_input("Neues Metadatum (Wert)")
        if new_key and new_value:
            new_metadata[new_key] = new_value
        
        submitted = st.form_submit_button("Speichern")
        if submitted:
            updates = {
                "temporary_id": temporary_id,
                "display_name": display_name,
                "notes": notes,
                "metadata": new_metadata
            }
            if update_dossier(dossier_id, updates):
                st.success("Dossier aktualisiert")
            else:
                st.error("Fehler beim Aktualisieren des Dossiers")
    
    # Statistiken
    st.subheader("Statistiken")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Emotionsstatistiken")
        plot_emotion_stats(dossier.get("emotion_stats", {}))
    
    with col2:
        st.write("Restraint-Statistiken")
        plot_restraint_stats(dossier.get("restraint_stats", {}))
    
    # Medienauftritte
    st.subheader("Medienauftritte")
    display_media_appearances(dossier.get("media_appearances", []))
    
    # Gesichtsinstanzen
    st.subheader("Gesichtsinstanzen")
    for face in dossier["face_instances"]:
        with st.expander(f"Gesicht {face['face_id']}"):
            col1, col2 = st.columns([1, 2])
            with col1:
                display_face_image(face)
            with col2:
                st.write(f"Job ID: {face['job_id']}")
                st.write(f"Media ID: {face['media_id']}")
                st.write(f"Quelle: {face['source_type']}")
                st.write(f"Zeitstempel: {datetime.fromisoformat(face['timestamp']).strftime('%Y-%m-%d %H:%M')}")
                
                if face.get('emotions'):
                    st.write("Emotionen:")
                    for emotion in face['emotions']:
                        for emotion_type, confidence in emotion.items():
                            st.write(f"- {emotion_type}: {confidence:.2f}")
                
                if face.get('restraints'):
                    st.write("Restraints:")
                    for restraint in face['restraints']:
                        for restraint_type, confidence in restraint.items():
                            st.write(f"- {restraint_type}: {confidence:.2f}")

def show_new_dossier():
    """Zeigt das Formular für neue Dossiers"""
    st.header("Neues Dossier erstellen")
    
    with st.form("new_dossier_form"):
        temporary_id = st.text_input("Temporäre ID")
        display_name = st.text_input("Anzeigename (optional)")
        notes = st.text_area("Notizen (optional)")
        
        submitted = st.form_submit_button("Dossier erstellen")
        if submitted and temporary_id:
            dossier = create_dossier(temporary_id)
            if dossier:
                st.success("Dossier erstellt")
                if display_name or notes:
                    updates = {
                        "display_name": display_name,
                        "notes": notes
                    }
                    update_dossier(dossier["dossier_id"], updates)
            else:
                st.error("Fehler beim Erstellen des Dossiers")
        elif submitted:
            st.error("Bitte geben Sie eine temporäre ID ein")

if __name__ == "__main__":
    main() 