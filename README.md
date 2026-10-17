# EN.601.661(02) Computer Vision - Course Project

- click [here](https://whiteboard.cloud.microsoft/me/whiteboards/p/c3BvOmh0dHBzOi8vbGl2ZWpvaG5zaG9wa2lucy1teS5zaGFyZXBvaW50LmNvbS9wZXJzb25hbC9hY2hlcnV2Ml9qaF9lZHU%3d/b!reAG3KHhS0aF67rzwluLoFWuxjk4lm5Gk9qaOkSgffEI5GWe4kiDT5oXWVzVnAmd/01DEIPJTX726LX3CGVOREZ3MOCWX6DKZ3L?fromShare=true) to write board
- click [here](https://jhu.instructure.com/courses/132294) to Canvas
- click [here](https://livejohnshopkins-my.sharepoint.com/:w:/g/personal/acheruv2_jh_edu/IQBN9RqY8ZXrRK03YlWsyuwFAWJvzYI30u94DS1zw56gDf4?e=qS2Mm1) to Pre-proposal (Shared Documents)
- click [here](https://livejohnshopkins-my.sharepoint.com/:w:/g/personal/acheruv2_jh_edu/IQDVjVXewHBqTK_FOWxEk8YUAZFaSJlUnDi15r1Neg-so4w?e=EetRBt) to Full Project Proposal (Shared Documents)

## Group members
- Alex Luna-Ow <alunaow1@jh.edu>
- Ahmed Cheruvattam <acheruv2@jh.edu> 
- Vincentz Luo <zluo46@jh.edu>
- Will Luo <yluo87@jh.edu>

## paper recommended
- Video-Based Surgical Tool-Tip and Keypoint Tracking Using Multi-Frame Context-Driven Deep Learning Models(https://shadowfax11.github.io/mfc_tracking/)
- SurgXBench: Explainable Vision-Language Model Benchmark for Surgery [https://arxiv.org/abs/2505.10764]
- Bridging Vision and Language for Robust Context-Aware Surgical Point Tracking: The VL-SurgPT Dataset and Benchmark: https://ojs.aaai.org/index.php/AAAI/article/view/38383?utm_source=chatgpt.com
- SRT-H: A hierarchical framework for autonomous surgery via language-conditioned imitation learning
(https://www.science.org/doi/full/10.1126/scirobotics.adt5254)
- ROBUST-MIPS: A Combined Skeletal Pose and Instance Segmentation Dataset for Laparoscopic Surgical Instruments: https://www.nature.com/articles/s41597-026-06938-5?utm_source=chatgpt.com

### Proposal requirement
- Problem Area - Describe the problem area and why it is important to research.
- Context - Write a paragraph on what others have done to solve this problem. Include some information on algorithms and their results. Use what you learned from the paper review too.
- Data - Include specific information of what data you will use. How much data will you have? What types of data?
- Proposed Solution - Write up a paragraph on your proposed solution. What algorithm(s) will you use? How will you evaluate the algorithms? What are the metrics you will use? What problems do you think you might encounter?

## Important Deadlines
| Assignment | Due Date | Points |
|---|---|--|
| Project Pre-proposal | October 5 | 5 |
| Homework 1 | October 12 | 100 |
| Project Full Proposal | October 19| 10 |
| Project Paper Review | October 26 | 10 |
| Project Midpoint Check-in | November 13 | 10 |
| Project Final Report | December 7 | 50 |
| Project Presentation (Slide Upload) | Not specified| Not specified |




## Instrument Tracking and Kinematics

### Goal

Identify and track surgical instrument tips across video frames sampled at fixed time intervals. Record each tip’s image coordinates consistently and use its trajectory to estimate velocity and speed in pixels per second.

Figure 1 illustrates the annotation of an instrument in a single frame, including a tip marker, a bounding box, and position and velocity information. Figure 2 illustrates how tracking the tip over time supports trajectory visualization and kinematic analysis.

<table>
  <tr>
    <td width="50%" align="center">
      <img src="./assets/fig1.png" width="100%" alt="Surgical instrument with a cyan bounding box, a tip marker, and an overlay showing position and velocity components.">
      <br>
      <strong>Figure 1. Single-frame instrument annotation.</strong>
      A cyan cross marks the selected tip location, while a bounding box indicates the instrument region. The overlay displays tip coordinates and image-plane velocity components.
    </td>
    <td width="50%" align="center">
      <img src="./assets/fig2.png" width="100%" alt="Instrument motion illustrated at three timestamps, with a trajectory overlay and plots of tip position and speed over time.">
      <br>
      <strong>Figure 2. Tool-tip tracking and kinematic visualization.</strong>
      Overlaid instrument positions at 0.0, 0.1, and 0.2 seconds illustrate motion over time. The lower panels show example position and speed curves.
    </td>
  </tr>
</table>

These figures illustrate the intended annotation and visualization concepts; the displayed values and curves should not be treated as validated measurements. The image coordinates labelled u and v correspond to x and y, respectively, in the notation below.

### Annotation Consistency

Consistent annotation requires the following:

- Track the same instrument across frames using a persistent instrument ID.
- Apply the same anatomical or geometric definition of the tool tip in every frame, including when the instrument jaws open or close.
- Use the same image coordinate system and image resolution throughout the analysis.
- Mark the tip as occluded or out of frame when its location cannot be reliably identified.

The tip marker in Figure 1 illustrates the point to be recorded. The sequence in Figure 2 illustrates why the same point definition must be maintained across time.

### Position

At sampled time step i, represent the tool-tip position as:

$$
\mathbf p_i=(x_i,y_i)
$$

The coordinates are measured in pixels. The origin is at the image’s upper-left corner, with x increasing to the right and y increasing downward.

As illustrated in Figure 1, tip coordinates can be displayed directly on the video frame. Recording these coordinates over time produces the position curves illustrated in Figure 2.

### Time Interval

For a constant-frame-rate video with frame rate f frames per second, consecutive frames are separated by:

$$
\Delta t=\frac{1}{f}
$$

If every k-th frame is labelled, the interval between labelled frames is:

$$
\Delta t=\frac{k}{f}
$$

The three overlaid positions in Figure 2 illustrate sampling at an interval of 0.1 seconds. For videos with irregular frame timing, use actual frame timestamps.

### Velocity

For equally spaced samples, estimate the velocity at labelled frame i using the central-difference formula:

$$
\mathbf v_i\approx
\frac{\mathbf p_{i+1}-\mathbf p_{i-1}}{2\Delta t}
\qquad \text{pixels/second}
$$

Here, i − 1 and i + 1 refer to the previous and next labelled samples, respectively.

The horizontal and vertical velocity components are:

$$
v_{x,i}\approx\frac{x_{i+1}-x_{i-1}}{2\Delta t},
\qquad
v_{y,i}\approx\frac{y_{i+1}-y_{i-1}}{2\Delta t}
$$

Figure 1 illustrates how these two components can be displayed alongside the instrument. Their signs indicate the direction of motion along each image axis.

This estimate requires valid tip positions at both neighbouring samples. Missing or occluded positions must be handled explicitly before calculating velocity.

### Speed

Speed measures how fast the tip moves, regardless of direction:

$$
s_i=\|\mathbf v_i\|
=\sqrt{v_{x,i}^{2}+v_{y,i}^{2}}
\qquad \text{pixels/second}
$$

The speed curve in Figure 2 illustrates how this quantity can be plotted over time. The scalar readout labelled “Tip velocity” in that figure should be interpreted as “Tip speed”; velocity itself has both horizontal and vertical components.

### Bounding Box

A bounding box may be recorded as an additional annotation to describe the instrument’s extent in the image, as illustrated in Figure 1.

The bounding-box centre is not necessarily the tool tip. Tip coordinates must therefore be labelled separately.

## Tool-Tip Detection and Tracking Pipeline 

### Approach 1

We will test pretrained **ConvNeXtSAM** on **CholecSeg8k RGB sequences** to estimate tool-tip-region displacement. These can be found here: https://github.com/FrancescoLeni/ConvNeXtSAM?utm_source=chatgpt.com and CholecSeg8K is pixel wise labelled dataset on kaggle here: https://www.kaggle.com/code/kerneler/starter-cholecseg8k-07367fcc-7/output

1. **Detect:** Run the detector on each frame to obtain bounding boxes and confidence scores.
2. **Locate:** Calculate each box center: `p = ((x1+x2)/2, (y1+y2)/2)`.
3. **Associate:** Match detections across frames using center distance and one-to-one assignment. Retain a unique `track_id` for each matched instrument.
4. **Calculate displacement:** For reliable consecutive matches, compute `Δp = p_current − p_previous`.
5. **Calculate velocity:** Divide displacement by elapsed time: `velocity = Δp / Δt`, in **pixels/second**. Use frame timestamps, or `Δt = (current_frame_index − previous_frame_index) / FPS` when the original frame rate and indices are verified. For consecutive frames at 25 FPS, `Δt = 0.04 s`.
6. **Export:** Overlay boxes, IDs, displacement, and velocity; save results to CSV.

Process each continuous sequence independently and reset tracks between folders. Leave displacement and velocity missing for new or uncertain matches. Use original timing when frames are sampled or skipped.

**Limitations:** Box centers approximate physical tip locations and are not the actual tip center, and detection jitter can produce noisy velocities. CholecSeg8k masks do not provide exact tip-point labels, so manual annotations are needed for evaluation. Image velocity includes camera motion; obtaining mm/s requires metric calibration and depth information.

### Approach 2: YOLO Pose for Tool-Tip Localization and Velocity

Train **YOLO Pose** using **EndoVis 2015 images and EndoVisPoseAnnotation keypoint labels** to predict instrument-tip coordinates directly. These can be found here: https://github.com/ultralytics/ultralytics/blob/main/README.md and https://github.com/surgical-vision/EndoVisPoseAnnotation?utm_source=chatgpt.com

data set for EndoVis 2015: https://archive.iar.kit.edu/opencas/index.html%3Fq%3Dnode%252F30.html?utm_source=chatgpt.com

1. **Prepare data:** Convert annotations into YOLO Pose format, including instrument boxes, keypoints, and visibility flags.
2. **Train:** Fine-tune the model to detect instruments and localize their landmarks, including jaw tips.
3. **Associate:** Run inference on consecutive frames and assign persistent instrument IDs through for reliable matching of the the keypoint across frames 
4. **Calculate motion:** For the same instrument and consistently defined tip point, calculate:
   - **Displacement:** `Δp = p_current − p_previous`
   - **Velocity:** `v = Δp / Δt` in **pixels/second**, using verified timestamps or original frame indices and FPS.
5. **Export:** Overlay boxes, tip points, IDs, and velocity; save results to CSV

Evaluate tip-location accuracy on held-out annotated frames. Reset tracks between sequences and omit velocity for missing or uncertain matches. Application to CholecSeg8k requires separate validation and may require fine-tuning. This approach replaces ConvNeXtSAM; optical flow is optional.
