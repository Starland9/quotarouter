"""
Streamlit app demonstrating QuotaRouter API integration.

This example shows how to use the QuotaRouter REST API
from a Streamlit web application.

Installation:
    pip install streamlit requests

Running:
    streamlit run 07_streamlit_integration.py

Then start the API server in another terminal:
    quotarouter api

The Streamlit app will communicate with the API at http://localhost:8000
"""

import json
import streamlit as st
import requests
from typing import Generator

# API configuration
API_BASE_URL = st.secrets.get("api_base_url", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="QuotaRouter Playground",
    page_icon="🔀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🔀 QuotaRouter - LLM Playground")
st.markdown(
    "Interactive playground for quota-aware LLM routing with automatic provider fallback."
)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_url = st.text_input(
        "API URL",
        value=API_BASE_URL,
        help="URL where QuotaRouter API is running",
    )

    st.divider()

    st.subheader("✨ Features")
    st.markdown(
        """
    - **Quota Management**: Automatic fallback to next provider
    - **Multiple Providers**: OpenRouter, Together AI, etc.
    - **Streaming**: Real-time response generation
    - **Book Generation**: Write entire books automatically
    """
    )

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["💬 Completion", "🌊 Streaming", "📊 Status", "📖 Book Generator"]
)

# ── Tab 1: Single Completion ────────────────────────────────────

with tab1:
    st.header("Single Completion")
    st.markdown("Generate a single response from the router.")

    col1, col2 = st.columns([3, 1])

    with col1:
        prompt = st.text_area(
            "Prompt",
            value="Explain quantum computing in simple terms",
            height=100,
            placeholder="Enter your prompt here...",
        )

    with col2:
        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=8000,
            value=500,
            step=100,
        )

    if st.button("🚀 Generate", use_container_width=True):
        with st.spinner("Generating..."):
            try:
                response = requests.post(
                    f"{api_url}/complete",
                    json={
                        "prompt": prompt,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                st.success("✅ Completion generated!")

                with st.container(border=True):
                    st.markdown("**Generated Text:**")
                    st.write(data["text"])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Provider", data["provider"])
                with col2:
                    st.metric("Tokens Used", data["tokens_used"])
                with col3:
                    st.metric("Stop Reason", data.get("stop_reason", "—"))

            except requests.exceptions.ConnectionError:
                st.error(
                    f"❌ Cannot connect to API at {api_url}. Is the server running?\n\nStart it with: `quotarouter api`"
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")


# ── Tab 2: Streaming ────────────────────────────────────────────

with tab2:
    st.header("Streaming Completion")
    st.markdown("Stream responses in real-time.")

    col1, col2 = st.columns([3, 1])

    with col1:
        stream_prompt = st.text_area(
            "Prompt",
            value="Write a short story about a robot",
            height=100,
            placeholder="Enter your prompt...",
            key="stream_prompt",
        )

    with col2:
        stream_temp = st.slider("Temperature", 0.0, 2.0, 0.8, 0.1, key="stream_temp")
        stream_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=8000,
            value=1000,
            step=100,
            key="stream_tokens",
        )

    if st.button("🌊 Stream Response", use_container_width=True):
        output_container = st.empty()
        status_container = st.empty()

        try:
            response = requests.post(
                f"{api_url}/stream",
                json={
                    "prompt": stream_prompt,
                    "temperature": stream_temp,
                    "max_tokens": stream_tokens,
                },
                stream=True,
                timeout=60,
            )
            response.raise_for_status()

            full_text = ""
            total_tokens = 0
            provider_used = None

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if not chunk.get("is_final"):
                        full_text += chunk["text"]
                        output_container.write(full_text)
                    else:
                        total_tokens = chunk.get("total_tokens", 0)
                        provider_used = chunk.get("provider", "unknown")

            with status_container.container(border=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Provider", provider_used or "—")
                with col2:
                    st.metric("Total Tokens", total_tokens)
                with col3:
                    st.metric("Characters", len(full_text))

        except requests.exceptions.ConnectionError:
            st.error(
                f"❌ Cannot connect to API at {api_url}. Is the server running?\n\nStart it with: `quotarouter api`"
            )
        except Exception as e:
            st.error(f"❌ Error: {e}")


# ── Tab 3: Provider Status ──────────────────────────────────────

with tab3:
    st.header("Provider Status & Quota")
    st.markdown("Monitor provider availability and quota usage.")

    if st.button("🔄 Refresh Status", use_container_width=True):
        try:
            response = requests.get(f"{api_url}/status", timeout=10)
            response.raise_for_status()
            data = response.json()

            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Active Provider", data["active_provider"])
            with col2:
                st.metric("Total Tokens", data["total_tokens_used"])
            with col3:
                st.metric("Total Requests", data["total_requests"])
            with col4:
                st.metric("Fallback Count", data["fallback_count"])

            st.divider()

            # Provider details
            st.subheader("Provider Details")
            for provider in data["providers"]:
                with st.expander(
                    f"**{provider['name']}** "
                    f"{'✅ Available' if provider['available'] else '❌ Exhausted'} "
                    f"({provider['quota_percentage']:.1f}% used)"
                ):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Tokens Used",
                            f"{provider['tokens_used']:,}",
                            f"/ {provider['token_limit'] or '∞'}",
                        )
                    with col2:
                        st.metric(
                            "Requests",
                            f"{provider['requests_used']:,}",
                            f"/ {provider['request_limit'] or '∞'} RPM",
                        )
                    with col3:
                        st.metric("Priority", provider["priority"])

                    # Progress bar
                    if provider["token_limit"]:
                        progress = provider["quota_percentage"] / 100
                        st.progress(
                            min(progress, 1.0),
                            text=f"{provider['quota_percentage']:.1f}% quota used",
                        )

        except requests.exceptions.ConnectionError:
            st.error(
                f"❌ Cannot connect to API at {api_url}. Is the server running?\n\nStart it with: `quotarouter api`"
            )
        except Exception as e:
            st.error(f"❌ Error: {e}")


# ── Tab 4: Book Generation ─────────────────────────────────────

with tab4:
    st.header("📖 Book Generator")
    st.markdown("Generate entire books automatically with chapter retry logic.")

    col1, col2 = st.columns(2)

    with col1:
        book_title = st.text_input(
            "Book Title",
            value="The Art of Python",
            placeholder="Enter book title...",
        )
        book_chapters = st.slider("Number of Chapters", 1, 20, 3)

    with col2:
        book_length = st.slider("Words per Chapter", 500, 5000, 2000, 100)
        book_style = st.selectbox(
            "Writing Style",
            ["educational", "narrative", "technical", "creative"],
            index=0,
        )

    if st.button("📝 Generate Book", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            with st.spinner(f"Generating {book_chapters} chapters..."):
                response = requests.post(
                    f"{api_url}/book",
                    json={
                        "title": book_title,
                        "chapters": book_chapters,
                        "chapter_length": book_length,
                        "style": book_style,
                    },
                    timeout=300,  # 5 minute timeout
                )
                response.raise_for_status()
                data = response.json()

                # Update progress
                progress = data["chapters_generated"] / data["total_chapters"]
                progress_bar.progress(progress)

                st.success(f"✅ Book generation complete!")

                # Results
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(
                            "Chapters",
                            f"{data['chapters_generated']}/{data['total_chapters']}",
                        )
                    with col2:
                        st.metric("Total Words", f"{data['total_words']:,}")
                    with col3:
                        st.metric("Tokens Used", f"{data['tokens_used']:,}")
                    with col4:
                        st.metric("Status", data["status"])

                    st.markdown(
                        f"**Providers Used:** {', '.join(data['providers_used'])}"
                    )

                    if data["filename"]:
                        st.markdown(f"**Saved to:** `{data['filename']}`")

        except requests.exceptions.ConnectionError:
            st.error(
                f"❌ Cannot connect to API at {api_url}. Is the server running?\n\nStart it with: `quotarouter api`"
            )
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Footer
st.divider()
st.markdown(
    """
---
Made with ❤️ by QuotaRouter  
[GitHub](https://github.com/Starland9/freerouter) | [Docs](https://github.com/Starland9/freerouter#readme)
"""
)
