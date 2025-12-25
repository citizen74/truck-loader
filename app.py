import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import random

# =========================
# ИНИЦИАЛИЗАЦИЯ SESSION STATE
# =========================

if "cargo_list" not in st.session_state:
    st.session_state["cargo_list"] = []

# =========================
# ЛОГИКА УПАКОВКИ (2D)
# =========================

class FreeRect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class PlacedItem:
    def __init__(self, name, x, y, w, h):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h


def pack_rectangles(container_w, container_h, items):
    items = sorted(items, key=lambda x: x["w"] * x["l"], reverse=True)

    free_rects = [FreeRect(0, 0, container_w, container_h)]
    placed = []
    not_placed = []

    for item in items:
        placed_flag = False

        for fr in free_rects:
            for (iw, ih) in [(item["w"], item["l"]), (item["l"], item["w"])]:
                if iw <= fr.w and ih <= fr.h:
                    placed.append(
                        PlacedItem(item["name"], fr.x, fr.y, iw, ih)
                    )

                    right = FreeRect(fr.x + iw, fr.y, fr.w - iw, ih)
                    top = FreeRect(fr.x, fr.y + ih, fr.w, fr.h - ih)

                    free_rects.remove(fr)
                    if right.w > 0 and right.h > 0:
                        free_rects.append(right)
                    if top.w > 0 and top.h > 0:
                        free_rects.append(top)

                    placed_flag = True
                    break

            if placed_flag:
                break

        if not placed_flag:
            not_placed.append(item)

    return placed, not_placed


# =========================
# ВИЗУАЛИЗАЦИЯ
# =========================

def draw(container_w, container_h, placed):
    fig, ax = plt.subplots(figsize=(12, 4))

    ax.add_patch(
        Rectangle((0, 0), container_w, container_h,
                  edgecolor="black", facecolor="none", linewidth=2)
    )

    for item in placed:
        color = (random.random(), random.random(), random.random())
        rect = Rectangle(
            (item.x, item.y),
            item.w,
            item.h,
            facecolor=color,
            edgecolor="black"
        )
        ax.add_patch(rect)
        ax.text(
            item.x + item.w / 2,
            item.y + item.h / 2,
            item.name,
            ha="center",
            va="center",
            fontsize=8
        )

    ax.set_xlim(0, container_w)
    ax.set_ylim(0, container_h)
    ax.set_aspect("equal")
    ax.set_title("Раскладка грузов (вид сверху)")
    ax.invert_yaxis()

    return fig


# =========================
# ИНТЕРФЕЙС
# =========================

st.title("🚚 Оптимизация загрузки кузова")

st.sidebar.header("Размеры кузова (метры)")
container_w = st.sidebar.number_input("Ширина", value=2.45)
container_l = st.sidebar.number_input("Длина", value=13.0)

st.header("Добавление груза")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    name = st.text_input("Название")
with col2:
    w = st.number_input("Ширина, м", min_value=0.01)
with col3:
    l = st.number_input("Длина, м", min_value=0.01)
with col4:
    h = st.number_input("Высота, м", min_value=0.01)
with col5:
    weight = st.number_input("Вес, кг", min_value=0.1)

qty = st.number_input("Количество", min_value=1, step=1)

if st.button("➕ Добавить груз"):
    for _ in range(qty):
        st.session_state["cargo_list"].append({
            "name": name,
            "w": w,
            "l": l,
            "h": h,
            "weight": weight
        })

# ===== Список грузов =====

if st.session_state["cargo_list"]:
    st.subheader("Список грузов")

    for i, item in enumerate(st.session_state["cargo_list"]):
        col1, col2, col3, col4, col5, col6 = st.columns([2,1,1,1,1,1])
        col1.write(item["name"])
        col2.write(f'{item["w"]}×{item["l"]}×{item["h"]}')
        col3.write(f'{item["weight"]} кг')
        col4.write(f'{item["w"]*item["l"]*item["h"]:.2f} м³')
        if col6.button("❌", key=f"del_{i}"):
            st.session_state["cargo_list"].pop(i)
            st.rerun()

# ===== Расчёт =====

if st.button("🚀 Рассчитать"):
    placed, not_placed = pack_rectangles(
        container_w,
        container_l,
        st.session_state["cargo_list"]
    )

    total_volume = sum(i["w"] * i["l"] * i["h"] for i in st.session_state["cargo_list"])
    total_weight = sum(i["weight"] for i in st.session_state["cargo_list"])

    used_area = sum(p.w * p.h for p in placed)
    total_area = container_w * container_l
    fill_percent = (used_area / total_area) * 100

    st.success(f"Заполнение площади: {fill_percent:.2f}%")
    st.info(f"📦 Общий объём: {total_volume:.2f} м³")
    st.info(f"⚖️ Общий вес: {total_weight:.1f} кг")

    st.pyplot(draw(container_w, container_l, placed))

    if not_placed:
        st.warning("❌ Не поместились:")
        st.table(not_placed)
    else:
        st.success("✅ Все грузы размещены")

if st.button("🧹 Очистить всё"):
    st.session_state["cargo_list"] = []
