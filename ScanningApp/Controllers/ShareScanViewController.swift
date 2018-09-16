/*
See LICENSE folder for this sample’s licensing information.

Abstract:
Customized share sheet for exporting scanned AR reference objects.
*/

import UIKit
import ARKit

func stringifyData(points: [float3]) -> String {
    var s = ""
    for f in points {
        print(f)
        s.append("\(f[0]), \(f[1]), \(f[2]) \n")
    }
    
    return s
}

func makeRequest () {
    let url = URL(string: "http://206.189.238.224:8078/hello")!
    var request = URLRequest(url: url)
    request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
    request.httpMethod = "POST"
    let postString = stringifyData(points: SavedPoints.points)
    request.httpBody = postString.data(using: .utf8)
    let task = URLSession.shared.dataTask(with: request) { data, response, error in
        guard let data = data, error == nil else {                                                 // check for fundamental networking error
            print("error=\(error)")
            return
        }
        
        if let httpStatus = response as? HTTPURLResponse, httpStatus.statusCode != 200 {           // check for http errors
            print("statusCode should be 200, but is \(httpStatus.statusCode)")
            print("response = \(response)")
        }
        
        let responseString = String(data: data, encoding: .utf8)
        print("responseString = \(responseString)")
    }
    task.resume()
}


class ShareScanViewController: UIActivityViewController {
    init(sourceView: UIView, sharedObject: Any) {
        super.init(activityItems: [sharedObject], applicationActivities: nil)
        
        print(SavedPoints.points)
        makeRequest()
        
        // Set up popover presentation style
        modalPresentationStyle = .popover
        popoverPresentationController?.sourceView = sourceView
        popoverPresentationController?.sourceRect = sourceView.bounds
        
        self.excludedActivityTypes = [.markupAsPDF, .openInIBooks, .message, .print,
                                      .addToReadingList, .saveToCameraRoll, .assignToContact,
                                      .copyToPasteboard, .postToTencentWeibo, .postToWeibo,
                                      .postToVimeo, .postToFlickr, .postToTwitter, .postToFacebook]
    }
    
    deinit {
        // Restart the session in case it was interrupted by the share sheet
        if let configuration = ViewController.instance?.sceneView.session.configuration,
            ViewController.instance?.state == .testing {
            ViewController.instance?.sceneView.session.run(configuration)
        }
    }
}
