SOURCE_URL = "http://bci.med.tsinghua.edu.cn/upload/zhangshangen"

ZIP_FILES_AND_SHA256SUMS = [
    ("S1-S10.mat.zip", "02893ac902dc9bb39e99e35f44f9c8cddb6b810a6f255ee33258c37fbd4ed08e"),
    ("S11-S20.mat.zip", "d137b6f4f861932701d3f4bf07b4a143c34095f5aabef2f9372be018e78956d3"),
    ("S21-S30.mat.zip", "6ac5f9cb7fead05942bbcc639cc28e648c5219b45c6624c838045ba26e29995d"),
    ("S31-S40.mat.zip", "c53f8400502175e2069e1645572852c0fc01d304fec060ccafe1394428044954"),
    ("S41-S50.mat.zip", "5f6d5fa5758ff00f630ddf87984ded56d42a271edc0c199f06d7d549609c2ab1"),
    ("S51-S60.mat.zip", "827429e2c3224860d33ae82d78ef52846882bd193176cf9edf5d4a27dec74ced"),
    ("S61-S64.mat.zip", "c500e8ef2062f71c3b7a929c26d1e6068fb73ede4593b7983d0bdb0fa8af51b3"),
]

ALL_FILES_AND_SHA256SUMS = [
    ("64-channels.loc", "947e5a743d86a5c94eaca6c442f1858f39d19486a5e841df4147063e15e9108c"),
    ("note.txt", "a70d6a729d861e8ad97dd1a6eb62f40bd93f32dca079d544ff9e269527d917f8"),
    ("Readme.txt", "5e67e6fe3596ff8b3691d812ab8ecf9286477d0b15361895c695977bebd57981"),
    ("subjects_information.xlsx", "beee4446bfdebd8d83fbe360ca4970525fd9921906b1dffab9ced99277aee68d"),
] + ZIP_FILES_AND_SHA256SUMS


WHICH_FOLDER_EACH_SUBJECT = {
    **{x: "S1-S10.mat" for x in range(1, 11)},
    **{x: "S11-S20.mat" for x in range(11, 21)},
    **{x: "S21-S30.mat" for x in range(21, 31)},
    **{x: "S31-S40.mat" for x in range(31, 41)},
    **{x: "S41-S50.mat" for x in range(41, 51)},
    **{x: "S51-S60.mat" for x in range(51, 61)},
    **{x: "S61-S64.mat" for x in range(61, 65)},
}
