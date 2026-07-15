import streamlit as st


def aplicar_estilo():
    st.markdown(
        """
        <style>
        :root {
            --azul-profundo: #071a3d;
            --azul: #0b4fc4;
            --azul-claro: #38bdf8;
            --amarelo: #ffd43b;
            --amarelo-hover: #ffbf00;
            --roxo: #8b5cf6;
            --texto: #f8fbff;
        }

        .stApp {
            background:
                radial-gradient(circle at 92% 8%, rgba(139, 92, 246, .28), transparent 28%),
                radial-gradient(circle at 8% 90%, rgba(56, 189, 248, .18), transparent 32%),
                linear-gradient(145deg, #06132f 0%, #08275d 52%, #10133f 100%);
            color: var(--texto);
        }

        [data-testid="stHeader"] {
            background: rgba(7, 26, 61, .72);
            backdrop-filter: blur(12px);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #061630 0%, #0b3474 62%, #24104f 100%);
            border-right: 1px solid rgba(255, 212, 59, .35);
            box-shadow: 8px 0 30px rgba(139, 92, 246, .16);
        }

        h1, h2, h3 {
            color: #ffffff;
            letter-spacing: -.02em;
            text-shadow: 0 3px 18px rgba(56, 189, 248, .22);
        }

        h1::after {
            content: "";
            display: block;
            width: 72px;
            height: 4px;
            margin-top: 10px;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--amarelo), var(--roxo));
            box-shadow: 0 0 18px rgba(139, 92, 246, .7);
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(145deg, rgba(15, 64, 140, .76), rgba(34, 20, 88, .72));
            border: 1px solid rgba(56, 189, 248, .28) !important;
            border-radius: 18px !important;
            box-shadow: 0 12px 32px rgba(2, 8, 23, .28), 0 0 22px rgba(139, 92, 246, .09);
            transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
            overflow: hidden;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-3px);
            border-color: rgba(255, 212, 59, .7) !important;
            box-shadow: 0 16px 38px rgba(2, 8, 23, .35), 0 0 25px rgba(139, 92, 246, .22);
        }

        div[data-testid="stForm"], div[data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(10, 53, 121, .74), rgba(45, 24, 103, .62));
            border: 1px solid rgba(56, 189, 248, .3);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 28px rgba(2, 8, 23, .24);
        }

        .stButton > button, .stFormSubmitButton > button {
            color: #071a3d;
            background: linear-gradient(135deg, #ffe56b, var(--amarelo));
            border: 1px solid rgba(255, 255, 255, .35);
            border-radius: 11px;
            font-weight: 800;
            box-shadow: 0 7px 18px rgba(255, 212, 59, .2);
            transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
        }

        .stButton > button:hover, .stFormSubmitButton > button:hover {
            color: #ffffff;
            background: linear-gradient(135deg, var(--roxo), #6d28d9);
            border-color: #c4b5fd;
            transform: translateY(-2px);
            box-shadow: 0 9px 25px rgba(139, 92, 246, .42);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(7, 26, 61, .45);
            border-radius: 13px;
            padding: 6px;
        }

        .stTabs [aria-selected="true"] {
            color: #071a3d !important;
            background: var(--amarelo) !important;
            border-radius: 9px;
            font-weight: 800;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        textarea {
            background-color: rgba(245, 249, 255, .96) !important;
            color: #071a3d !important;
            border-color: rgba(56, 189, 248, .65) !important;
        }

        div[data-baseweb="input"] input,
        div[data-baseweb="select"] *, textarea {
            color: #071a3d !important;
        }

        [data-testid="stFileUploaderDropzone"] {
            background: rgba(11, 79, 196, .22);
            border: 1px dashed var(--amarelo);
            border-radius: 14px;
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
            border-left: 4px solid var(--amarelo);
        }

        .image-placeholder {
            min-height: 150px;
            display: grid;
            place-items: center;
            font-size: 64px;
            border-radius: 13px;
            background: linear-gradient(135deg, rgba(56, 189, 248, .2), rgba(139, 92, 246, .32));
            border: 1px solid rgba(255, 212, 59, .24);
        }

        [data-testid="stImage"] img {
            max-height: 230px;
            object-fit: cover;
            border-radius: 13px;
        }

        #MainMenu, footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )
