#!/usr/env/bin/python
"""
JSON形式で保存したボディトラッキング情報を、3D散布図にプロットするスクリプト
入力と同じファイル名のgif画像がgifsフォルダに保存されます。
args:
    --path(str): JSONファイルのパス
    --print_keypoint_name(str): 各キーポイントのラベルを出力するかどうか("True": 出力する, "False": 出力しない)
"""


import argparse
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os

def json_to_ndarray(json_path: str) -> ("np.ndarray[np.ndarray[float]]", "np.ndarray[np.ndarray[float]]", "np.ndarray[np.ndarray[float]]", "np.ndarray[np.ndarray[str]]"):
    """objファイルからデータを読みだして配列に直す
    args:
        json_path(str): データが保存されているjsonファイルのパス
    return:
        x("np.ndarray[np.ndarray[float]]"): 各キーポイントのx座標
        y("np.ndarray[np.ndarray[float]]"): 各キーポイントのy座標
        z("np.ndarray[np.ndarray[float]]"): 各キーポイントのz座標
        label("np.ndarray[np.ndarray[str]]"): 各キーポイントのラベル名
    """
    x = []
    y = []
    z = []
    labels = []

    with open(json_path) as jfs:
        for data_str in jfs:
            x_per_frame = []
            y_per_frame = []
            z_per_frame = []
            label_per_frame = []

            try:
                data_obj = json.loads(data_str)
                keypoints = data_obj["Bones"]
                for keypoint in keypoints:
                    x_per_frame.append(keypoint["Position"]["x"])
                    y_per_frame.append(keypoint["Position"]["y"])
                    z_per_frame.append(keypoint["Position"]["z"])
                    label_per_frame.append(keypoint["Name"])
            except EOFError as e:
                break
            
            x.append(x_per_frame)
            y.append(y_per_frame)
            z.append(z_per_frame)
            labels.append(label_per_frame)
    
    return (
        np.array(x),
        np.array(y),
        np.array(z),
        np.array(labels)
    )

def get_scatter_scale(x: "np.ndarray[np.ndarray[float]]", y: "np.ndarray[np.ndarray[float]]", z: "np.ndarray[np.ndarray[float]]") -> "np.ndarray[np.ndarray[float]]":
    """x, y, z座標からグラフのプロットに適切なスケールを求める
    args:
        x("np.ndarray[np.ndarray[float]]"): キーポイントのx座標
        y("np.ndarray[np.ndarray[float]]"): キーポイントのy座標
        z("np.ndarray[np.ndarray[float]]"): キーポイントのz座標
    return:
        lim("np.ndarray[np.ndarray[float]]"): x, y, z座標軸の上限と下限
    """
    max_range = np.array([np.amax(x) - np.amin(x), np.amax(y) - np.amin(y), np.amax(z) - np.amin(z)]).max() * 0.5

    mid_x = (np.amax(x) + np.amin(x)) * 0.5
    mid_y = (np.amax(y) + np.amin(y)) * 0.5
    mid_z = (np.amax(z) + np.amin(z)) * 0.5

    return np.array([
        [mid_x - max_range, mid_x + max_range],
        [mid_y - max_range, mid_y + max_range],
        [mid_z - max_range, mid_z + max_range]
    ])



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str)
    parser.add_argument("print_keypoint_name", type=str, default="False")
    args = parser.parse_args()

    x, y, z, labels = json_to_ndarray(args.path)

    lim = get_scatter_scale(x, y, z)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    # 軸ラベルを設定(y, zを入れ替え)
    ax.set_xlabel('x')
    ax.set_ylabel('z')
    ax.set_zlabel('y')
    ax.set_xlim(lim[0][0], lim[0][1])
    ax.set_ylim(lim[2][0], lim[2][1])
    ax.set_zlim(lim[1][0], lim[1][1])
    ax.set_aspect("equal")

    def return_animation(i) -> None:
        """i番目のフレームのキーポイントをプロットする関数
        args:
            i(int): フレーム番号
        """
        print("processing: {}/{}".format(i, len(x)))
        ax.cla()
        ax.scatter(x[i], z[i], y[i])
        if args.print_keypoint_name == "True":
            for j, label in enumerate(labels[i]):
                ax.text(x[i][j], z[i][j], y[i][j], label)
    
    ani = animation.FuncAnimation(fig, func=return_animation, frames=len(x), interval=500)
    output_file_name = os.path.split(args.path)[-1].split('.')[0]

    ani.save("gifs/{}.gif".format(output_file_name), writer="pillow")

    plt.show()
