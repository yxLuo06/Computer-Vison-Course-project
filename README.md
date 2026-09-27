# Computer-Vison-Course-project
## Instrument Tracking and Kinematics

Goal: Kinematic labelling of surgical instrument tips

Identify and track the tip of each surgical instrument across video frames sampled at fixed time intervals. Record the tip’s image coordinates consistently and use its trajectory to estimate velocity in pixels per second.

What does “consistently” mean?

- Track the same instrument across frames using a persistent instrument ID.
- Apply the same definition of the tool tip in every frame.
- Use the same image coordinate system throughout the video.
- Mark the tip as occluded or out of frame when its location cannot be reliably identified.

---

### Position

At time step i, represent the tool-tip position as:

$$
\mathbf p_i=(x_i,y_i)
$$

Here, x and y are image coordinates measured in pixels. A common convention is to place the origin at the image’s upper-left corner, with x increasing to the right and y increasing downward.

### Time interval

For a constant-frame-rate video with frame rate f frames per second, consecutive frames are separated by:

$$
\Delta t=\frac{1}{f}
$$

If every k-th frame is labelled, the time interval between labelled frames is:

$$
\Delta t=\frac{k}{f}
$$

### Velocity

Estimate the velocity at labelled frame i using the central-difference formula, where i − 1 and i + 1 denote the previous and next labelled frames:

$$
\mathbf v_i\approx
\frac{\mathbf p_{i+1}-\mathbf p_{i-1}}{2\Delta t}
\qquad \text{pixels/second}
$$

Equivalently:

$$
v_{x,i}\approx\frac{x_{i+1}-x_{i-1}}{2\Delta t},
\qquad
v_{y,i}\approx\frac{y_{i+1}-y_{i-1}}{2\Delta t}
$$

The speed, which measures how fast the tip moves regardless of direction, is:

$$
s_i=\|\mathbf v_i\|
=\sqrt{v_{x,i}^{2}+v_{y,i}^{2}}
$$

Bounding box: optional additional annotation

A bounding box can also be recorded to indicate the instrument’s extent in the image. However, the bounding-box centre is not necessarily the tool tip; tip coordinates should be labelled separately.
