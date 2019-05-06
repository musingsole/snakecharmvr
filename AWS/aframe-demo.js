function create(){
    var sceneEl = document.querySelector('a-scene');
    var hinge = document.createElement("a-entity")
    var arm = document.createElement("a-entity")

    hinge.setAttribute('id', 'hinge')
    hinge.setAttribute('position', '0, 1, -5')
    hinge.setAttribute('rotation', "90 0 0")
    hinge.setAttribute('geometry', "primitive: cylinder; height: 1; radius: 0.25;")
    hinge.setAttribute('material', "color: #AB3CF2")

    sceneEl.appendChild(hinge)

    arm.setAttribute('id', 'arm')
    arm.setAttribute('position', '0, 2, -5.05')
    arm.setAttribute('geometry', 'primitive: box; depth: 0.9; height: 2; width: 0.4')
    arm.setAttribute('material', 'color: #DEADBE')

    sceneEl.appendChild(arm)
}


function animate(){
    var arm = document.querySelector('#servoarm')
    arm.setAttribute("animation__zam", "property: rotation; to: 0 0 -360; dir: alternate; loop: true; dur: 10000")
}

function aframe_change_color_on_hover() {
    var data = this.data;
    var el = this.el; 

    if (data != null && el != null){
        var defaultMaterial = el.getAttribute('default_material');

        el.addEventListener('mouseenter', function () {
          el.setAttribute('material', data);
        });

        el.addEventListener('mouseleave', function () {
          el.setAttribute('material', defaultMaterial);
        })
    }
}
