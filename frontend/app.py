import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

def send_chat(messages):
    """
    Send the chat transcript to the backend and return the assistant's reply.


    messages: list[{"role": str, "content": str}]
    returns: str (assistant reply)
    """
    payload = {"messages": messages}
    r = requests.post(f"{BACKEND_URL}/chat/details", json=payload, timeout=60)
    r.raise_for_status()
    return r.json().get("response", "")

def main():

    st.set_page_config(page_title="Speciphic Tutor", layout="wide")
    # Options for the selectbox
    options_list = ["Consumer Edge"]
    st.sidebar.image("logo.png", width='stretch')
    app_name = st.sidebar.selectbox(
        "Choose an option:",
        options_list
    )
    st.title("Speciphic Tutor: "+app_name)
    # Add a menu to select different options

    tab1, tab2, tab3 = st.tabs(
        ["## Overview of Consumer Edge", "## Technical Details", "## Video Library"])
    with tab1:

        st.write("""
        In today’s digital marketplace, conversations with consumers rarely follow a straight line. 
        Questions, frustrations, and requests arrive in many forms — and too often, brands struggle 
        to respond quickly and effectively. Enter **Consumer Edge**, a new AI-powered application 
        designed to transform how companies like Del Monte and Tropicana connect with their customers.
        """)

        st.markdown(
            '<div style="text-align: center;">'
            '<img src="https://static.businessworld.in/Untitled%20design%20-%202024-09-13T094209.522_20240913105508_original_image_15.webp" width="30%">'
            '<p><em>AI transforming conversations</em></p>'
            '</div>',
            unsafe_allow_html=True
        )

        st.write("""
        At its core, Consumer Edge acts as a smart conversational partner. 
        Customers interact naturally through chat, while the AI listens for intent, sentiment, 
        and needs hidden between the lines. If someone hints at frustration, the system can instantly 
        trigger a feedback form. If a shopper is searching for a favorite juice flavor, it can 
        launch a product locator. By seamlessly rerouting conversations to the right action items, 
        Consumer Edge minimizes friction and maximizes satisfaction.
        """)

        st.write("""
        For Del Monte and Tropicana, the advantages are clear. Instead of asking consumers to 
        navigate complex menus or wait on hold, the platform adapts in real time — surfacing the 
        right tool or solution at the right moment. It is more than just automation; it is a way 
        to **meet consumers where they are** and ensure their voice translates directly into action.
        """)

        st.markdown(
            '<div style="text-align: center;">'
            '<img src="https://www.agilitypr.com/wp-content/uploads/2024/06/cx-1.jpg" width="30%">'
            '<p><em>Seamless customer journeys</em></p>'
            '</div>',
            unsafe_allow_html=True
        )

        st.write("""
        The impact goes beyond individual chats. Aggregated insights from thousands of interactions 
        help brands spot recurring issues, identify trending requests, and measure sentiment shifts. 
        That means companies can respond not only to the customer in front of them but also to the 
        broader market pulse.  

        With Consumer Edge, every conversation is an opportunity — not just to solve a problem, 
        but to strengthen loyalty, sharpen insights, and build trust.
        """)

        #st.caption("— End of Overview —")

    with tab2:

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        st.markdown("### What would you like to know?")

        # ---- Chat history in a fixed-height scrollable container ----
        chat_box = st.container(height=420, border=True)  # adjust height to taste
        with chat_box:
            for msg in st.session_state["messages"]:
                with st.chat_message(
                    msg["role"],
                    avatar="user.svg" if msg["role"] == "user" else "logo.svg"
                ):
                    st.markdown(msg["content"])

        # ---- Input always below the chat history container ----
        if prompt := st.chat_input("Type your message...", key="tech_chat_input"):
            # Add user message and render instantly
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_box:
                with st.chat_message("user", avatar="user.svg"):
                    st.markdown(prompt)

            # Call backend with full transcript
            try:
                with st.spinner("Contacting assistant…"):
                    reply = send_chat(st.session_state.messages)
            except Exception as e:
                reply = f"Error contacting backend: {e}"

            # Add assistant reply and render
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with chat_box:
                with st.chat_message("assistant", avatar="logo.png"):
                    st.markdown(reply)
        
        
        # --- Knowledge Base Below ---
        st.markdown("---")

        st.markdown("## Knowledge Base Articles")

        st.title("Support & Maintenance Plan")

        with st.expander("1. Overview"):
            st.write("""
            This Support & Maintenance Plan defines the scope, responsibilities, and procedures for ongoing support, 
            issue resolution, software updates, and maintenance services. It ensures continuous system reliability 
            and optimal performance.
            """)

        with st.expander("2. Support Services"):
            st.subheader("2.1 Support Tiers & Response Times")
            st.write("""
            Support is categorized by severity to ensure timely response and resolution:
            """)
            st.table({
                "Severity Level": ["Critical (P1)", "High (P2)", "Medium (P3)", "Low (P4)"],
                "Description": [
                    "System completely down or major disruption affecting business operations.",
                    "Significant functionality impaired; workaround available.",
                    "Minor issue with limited functional impact.",
                    "General inquiry, enhancement request, or cosmetic issue."
                ],
                "Response Time": ["Within 2 hours", "Within 4 hours", "Within 1 business day", "Within 2 business days"],
                "Resolution Time": ["4–8 hours", "1–2 business days", "3–5 business days", "As per roadmap"]
            })

            st.subheader("2.2 Support Channels")
            st.write("""
            Support is available through the following channels:

            - **Email Support:** support@flexday.ai  
            - **Phone Support:** +1-XXX-XXX-XXXX  
            *Available during business hours (Time Zone: [Specify])*
            """)

        with st.expander("3. Bug Fixing & Patch Management"):
            st.subheader("3.1 Issue Reporting")
            st.write("""
            - Clients must report issues via email with:
                - Detailed issue description  
                - Screenshots (if applicable)  
                - Steps to reproduce the issue  
            - Each issue will receive a unique tracking ID for reference.
            """)

            st.subheader("3.2 Resolution Process")
            st.write("""
            - Issues will be categorized based on severity and handled per SLA timelines.  
            - Fixes will first be tested in a staging environment before deployment to production.  
            - Emergency hotfixes will be applied immediately if necessary.
            """)

        with st.expander("4. Software Updates & Upgrades"):
            st.subheader("4.1 Release Schedule")
            st.write("""
            - **Minor Updates & Patches:** Quarterly or as needed for bug fixes and small improvements.  
            - **Major Releases:** Annually or as per client requirements, including new features or architectural upgrades.
            """)

            st.subheader("4.2 Compatibility & Versioning")
            st.write("""
            - Updates will maintain backward compatibility, unless specified otherwise.  
            - Clients will receive advance notice for any breaking changes.
            """)

        with st.expander("5. Performance Monitoring & Optimization"):
            st.subheader("5.1 System Health Monitoring")
            st.write("""
            - Automated tools will track uptime, performance, and error rates.  
            - Alerts will be triggered for anomalies, with proactive fixes implemented promptly.  
            - See *Monitoring, Security, and Compliance* for additional details.
            """)

            st.subheader("5.2 Performance Optimization")
            st.write("""
            - Regular system assessments will identify and resolve performance bottlenecks.  
            - Clients will receive quarterly performance reports.
            """)

        with st.expander("6. Escalation Matrix"):
            st.write("""
            | **Escalation Level** | **Contact Person** | **Response Time** |
            |----------------------|--------------------|------------------|
            | Level 1 | Support Engineer | Within standard SLA times |
            | Level 2 | Senior Engineer | Additional 24 hours |
            | Level 3 | Technical Lead | Additional 48 hours |
            | Level 4 | Support Manager | Immediate attention |
            """)

        with st.expander("7. Client Responsibilities"):
            st.write("""
            Clients are responsible for:
            - Providing necessary system access and information for troubleshooting.  
            - Ensuring the software operates within recommended infrastructure and load conditions.
            """)

    with tab3:

        # Helper to display videos in a 3-column grid
        def show_videos(title, videos):
            st.markdown(f"### {title}")
            cols = st.columns(3)
            for i, video in enumerate(videos):
                with cols[i % 3]:
                    st.video(video)

        st.markdown("### 🎬 Consumer Edge Movie")
        left, center, right = st.columns([1, 2, 1])  # middle column wider
        with center:
            st.video("https://www.youtube.com/watch?v=dE377_5q3qA")

        def show_videos(title, video_urls):
            with st.expander(title, expanded=True):
                # create one column per video
                cols = st.columns(len(video_urls))
                for col, url in zip(cols, video_urls):
                    # Convert Shorts URL to watchable format if needed
                    if "/shorts/" in url:
                        url = url.replace("shorts/", "watch?v=")
                    col.video(url)

        # --- Section 3: Shorts ---
        show_videos("🎥 Highlights", [
            "https://youtube.com/shorts/LH7hx_7hqOg?si=6LpYloXckyALZet0",   # AI Short
            "https://youtube.com/shorts/ON6wVE37zBA?si=NCqNP835wG2jlcLC",   # AI Innovation
            "https://youtube.com/shorts/-S8AhV36BLE?si=OM-BiljQOKcOydBG"    # AI in Everyday Life
        ])


if __name__ == "__main__":
    main()
