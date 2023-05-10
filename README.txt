# A2 Notes
    Yongjia Huang(y649huan 20842254)

    ## Setup
    * macOS 13.2.1
    * Python 3.7.3

    ## Instruction
    * change permission
        chmod +x receiver
        chmod +x sender
    * Execution:
        1. On the host host1: ./nEmulator 9991 host2 9994 9993 host3 9992 1 0.2 0
        2. On the host host2: ./receiver host1 9993 9994 <output File>
        3. On the host host3: ./sender host1 9991 9992 50 <input file>
        run command in givien order
    * Find usage instructions of network_emulator.py using: ./nEmulator -h
    * Find usage instructions of receiver.py using: ./receiver -h
    * Find usage instructions of sender.py using: ./sender -h

    ## Testing (Machine)
    * testing on same machine:
        nEmulator: ubuntu2004-002.student.cs.uwaterloo.ca (hostname: ubuntu2004-002)
        receiver: ubuntu2004-002.student.cs.uwaterloo.ca (hostname: ubuntu2004-002)
        sender: ubuntu2004-002.student.cs.uwaterloo.ca (hostname: ubuntu2004-002)
    * testing on two different machines:
        nEmulator: ubuntu2004-002.student.cs.uwaterloo.ca (hostname: ubuntu2004-002)
        receiver: ubuntu2004-002.student.cs.uwaterloo.ca (hostname: ubuntu2004-002)
        sender: ubuntu2004-004.student.cs.uwaterloo.ca (hostname: ubuntu2004-004)

        or

        nEmulator: ubuntu2004-002.student.cs.uwaterloo.ca (hostname: ubuntu2004-002)
        receiver: ubuntu2004-004.student.cs.uwaterloo.ca (hostname: ubuntu2004-004)
        sender: ubuntu2004-002.student.cs.uwaterloo.ca (hostname: ubuntu2004-002)

        or

        nEmulator: ubuntu2004-004.student.cs.uwaterloo.ca (hostname: ubuntu2004-004)
        receiver: ubuntu2004-002.student.cs.uwaterloo.ca (hostname: ubuntu2004-002)
        sender: ubuntu2004-002.student.cs.uwaterloo.ca (hostname: ubuntu2004-002)
    * testing on three different machines:
        nEmulator: ubuntu2004-002.student.cs.uwaterloo.ca (hostname: ubuntu2004-002)
        receiver: ubuntu2004-004.student.cs.uwaterloo.ca (hostname: ubuntu2004-004)
        sender: ubuntu2004-008.student.cs.uwaterloo.ca (hostname: ubuntu2004-008)
